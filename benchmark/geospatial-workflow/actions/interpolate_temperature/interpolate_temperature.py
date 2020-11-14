import io
import math
import numpy as np
import pandas as pd
import rasterio
import time
import os
from rasterio.windows import Window
from types import SimpleNamespace
from scipy.spatial import distance_matrix
from shapely.geometry import Point, MultiPoint, box

from cos_backend import COSBackend


def compute_basic_interpolation(shape, stations, field_value='tdet', offset=(0, 0)):
    station_pixels = [[pixel[0], pixel[1]] for pixel in stations['pixel'].to_numpy()]
    # Get an array where each position represents pixel coordinates
    tile_pixels = np.indices(shape).transpose(1, 2, 0).reshape(shape[0] * shape[1], 2) + offset
    dist = distance_matrix(station_pixels, tile_pixels)
    weights = np.where(dist == 0, np.finfo('float32').max, 1.0 / dist)
    weights /= weights.sum(axis=0)
    return np.dot(weights.T, stations[field_value].to_numpy()).reshape(shape).astype('float32')


def compute_interpolated_temperature(elevations, stations, zdet, r, offset=(0, 0)):
    return compute_basic_interpolation(elevations.shape, stations, 'tdet', offset) + \
           r * (elevations - zdet)


def filter_stations(area_of_influence, bounds, stations):
    total_points = MultiPoint([Point(x, y) for x, y in stations[['X', 'Y']].to_numpy()])
    intersection = bounds.buffer(area_of_influence).intersection(total_points)
    return stations[[intersection.contains(point) for point in total_points]]


def map_interpolation(siam_stream, mdt, block_x, block_y, splits, zdet, r, area_of_influence):
    siam = pd.read_csv(io.BytesIO(siam_stream.read()))

    print('Importing mdt file...')
    with rasterio.open(mdt) as src:
        print('Ok')
        transform = src.transform
        # Compute working window
        step_w = src.width / splits
        step_h = src.height / splits
        offset_h = round(step_h * block_x)
        offset_w = round(step_w * block_y)
        profile = src.profile
        width = math.ceil(step_w * (block_y + 1) - offset_w)
        height = math.ceil(step_h * (block_x + 1) - offset_h)
        profile.update(width=width)
        profile.update(height=height)
        window = Window(offset_w, offset_h, width, height)
        bounding_rect = box(src.bounds.left, src.bounds.top, src.bounds.right, src.bounds.bottom)
        filtered = pd.DataFrame(filter_stations(area_of_influence, bounding_rect, siam))
        filtered['pixel'] = filtered.apply(
            lambda station: rasterio.transform.rowcol(transform, station['X'], station['Y']), axis=1)
        # Interpolate and write results
        with rasterio.open('output', "w", **profile) as dest:
            elevations = src.read(1, window=window)  # Get elevations content
            interpolation = compute_interpolated_temperature(elevations, filtered, zdet, r,
                                                             (offset_h, offset_w))
            dest.write(np.where(elevations == src.nodata, np.nan, interpolation), 1)

    return 'output'


def main(args):
    start_time = time.time()
    args.update(args['chunk'])
    parameters = SimpleNamespace(**args['parameters'])
    cos = COSBackend(aws_access_key_id=args['cos']['aws_access_key_id'],
                     aws_secret_access_key=args['cos']['aws_secret_access_key'],
                     endpoint_url=args['cos']['private_endpoint'])

    mdt_key = args['mdt_key']
    mdt = cos.get_object(key=mdt_key, bucket=parameters.BUCKET)
    siam_stream = cos.get_object(key='siam_out.csv', bucket=parameters.BUCKET)

    out = map_interpolation(siam_stream=siam_stream, mdt=mdt,
                            block_x=args['block_x'], block_y=args['block_y'], splits=parameters.SPLITS,
                            zdet=parameters.zdet, r=parameters.r, area_of_influence=parameters.AREA_OF_INFLUENCE)

    result_key = '/'.join(['tmp', 'TEMPERATURE',
                           os.path.basename(mdt_key).rsplit('.')[0],
                           str(args['block_x']) + '_' + str(args['block_y']) + '.tif'])

    cos.upload_file(filename=out, bucket=parameters.BUCKET, key=result_key)
    end_time = time.time()
    return {'result': result_key, 'start_time': start_time, 'end_time': end_time}
