from functools import partial
from types import SimpleNamespace
import rasterio
import fiona
import math
import time
from shapely.geometry import shape, box
from rasterio import features
from rasterio.windows import Window
import numpy as np

# from cos_backend import COSBackend

vineyard = ['VI', 'VO', 'VF', 'FV', 'CV']
olive_grove = ['OV', 'VO', 'OF', 'FL', 'OC']
fruit = ['FY', 'VF', 'OF', 'FF', 'CF']
nuts = ['FS', 'FV', 'FL', 'FF', 'CS']
citrus = ['CI', 'CV', 'OC', 'CF', 'CS']


def get_kc(feature):
    # TODO: Get more precise values of Kc
    if 'uso_sigpac' in feature['properties']:
        sigpac_use = feature['properties']['uso_sigpac']
        if sigpac_use in vineyard:
            # Grapes for wine - 0.3, 0.7, 0.45
            return 0.7
        if sigpac_use in olive_grove:
            # Olive grove - ini: 0.65, med: 0.7, end: 0.7
            return 0.7
        if sigpac_use in fruit:
            # Apples, Cherries, Pears - 0.45, 0.95, 0.7
            return 0.95
        if sigpac_use in nuts:
            # Almonds - 0.4, 0.9, 0.65
            return 0.9
        if sigpac_use in citrus:
            # Citrus, without ground coverage - 0.7, 0.65, 0.7
            return 0.65

    return None


def get_geometry_window(src, geom_bounds):
    left, bottom, right, top = geom_bounds
    src_left, src_bottom, src_right, src_top = src.bounds
    window = src.window(max(left, src_left), max(bottom, src_bottom), min(right, src_right), min(top, src_top))
    window_floored = window.round_offsets(op='floor', pixel_precision=3)
    w = math.ceil(window.width + window.col_off - window_floored.col_off)
    h = math.ceil(window.height + window.row_off - window_floored.row_off)
    return Window(window_floored.col_off, window_floored.row_off, w, h)


def compute_crop_evapotranspiration(temperatures, humidities, wind_speeds, external_radiations, global_radiations, KCs):
    gamma = 0.665 * 101.3 / 1000
    eSat = 0.6108 * np.exp((17.27 * temperatures) / (temperatures + 237.3))
    delta = 4098 * eSat / np.power((temperatures + 237.3), 2)
    eA = np.where(humidities < 0, 0, eSat * humidities / 100)  # Avoid sqrt of a negative number
    T4 = 4.903 * np.power((273.3 + temperatures), 4) / 1000000000
    rSrS0 = global_radiations / (external_radiations * 0.75)
    rN = 0.8 * global_radiations - T4 * (0.34 - 0.14 * np.sqrt(eA)) * ((1.35 * rSrS0) - 0.35)
    den = delta + gamma * (1 + 0.34 * wind_speeds)
    tRad = 0.408 * delta * rN / den
    tAdv = gamma * (900 / (temperatures + 273)) * wind_speeds * (eSat - eA) / den
    return ((tRad + tAdv) * 7 * KCs).astype('float32')


def compute_evapotranspiration_by_shape(tem, hum, win, rad, extrad, dst):
    non_arable_land = ['AG', 'CA', 'ED', 'FO', 'IM', 'PA', 'PR', 'ZU', 'ZV']

    with fiona.open('zip://shape.zip') as shape_src:
        for feature in shape_src.filter(bbox=tem.bounds):
            KC = get_kc(feature)
            if KC is not None:
                geom = shape(feature['geometry'])
                window = get_geometry_window(tem, geom.bounds)
                win_transform = rasterio.windows.transform(window, tem.transform)
                # Convert shape to raster matrix
                image = features.rasterize([geom],
                                           out_shape=(window.height, window.width),
                                           transform=win_transform,
                                           fill=0,
                                           default_value=1).astype('bool')
                # Get values to compute evapotranspiration
                temperatures = tem.read(1, window=window)
                humidities = hum.read(1, window=window)
                wind_speeds = win.read(1, window=window)
                # Convert from W to MJ (0.0036)
                global_radiations = rad.read(1, window=window) * 0.0036
                external_radiations = extrad.read(1, window=window) * 0.0036
                KCs = np.full(temperatures.shape, KC)
                # TODO: compute external radiation
                # external_radiations = np.full(temperatures.shape, 14)
                # TODO: compute global radiation
                # global_radiations = np.full(temperatures.shape, 10)
                etc = compute_crop_evapotranspiration(
                    temperatures,
                    humidities,
                    wind_speeds,
                    external_radiations,
                    global_radiations,
                    KCs
                )
                etc[temperatures == tem.nodata] = dst.nodata
                etc[np.logical_not(image)] = dst.nodata
                dst.write(etc + dst.read(1, window=window), 1, window=window)


def combine_calculations(tile, temperature, humidity, wind, radiance, extrad):
    with rasterio.open(temperature) as tem:
        profile = tem.profile
        profile.update(nodata=0)
        with rasterio.open(humidity) as hum:
            with rasterio.open(wind) as win:
                with rasterio.open(radiance) as rad:
                    with rasterio.open(extrad) as ext_rad:
                        with rasterio.open('output', 'w+', **profile) as dst:
                            # compute_global_evapotranspiration(tem, hum, win, rad, extrad, dst)
                            compute_evapotranspiration_by_shape(tem, hum, win, rad, ext_rad, dst)

    return 'output'


def main(args):
    start_time = time.time()
    parameters = SimpleNamespace(**args['parameters'])
    # cos = COSBackend(aws_access_key_id=args['cos']['aws_access_key_id'],
    #                  aws_secret_access_key=args['cos']['aws_secret_access_key'],
    #                  endpoint_url=args['cos']['private_endpoint'])

    tile = args['tile']

    # Download shapefile
    # shapefile = cos.get_object(bucket=parameters.BUCKET, key='shapefile.zip')
    with open('shape.zip', 'wb') as shapf:
        for chunk in iter(partial(shapefile.read, 200 * 1024 * 1024), ''):
            if not chunk:
                break
            shapf.write(chunk)

    rasters = {}
    for type in ['TEMPERATURE', 'HUMIDITY', 'WIND', 'EXTRAD', 'RADIANCE']:
        key = '/'.join(['tmp', type, tile, 'merged.tif'])
        rasters[type.lower()] = cos.get_object(bucket=parameters.BUCKET, key=key)

    filename = combine_calculations(tile=tile, **rasters)

    result_key = '/'.join(['tmp', 'ETC', args['tile'] + '.tif'])
    # cos.upload_file(filename=filename, bucket=parameters.BUCKET, key=result_key)
    end_time = time.time()
    return {'result': filename, 'start_time': start_time, 'end_time': end_time}
