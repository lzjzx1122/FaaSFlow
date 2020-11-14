from types import SimpleNamespace
import rasterio
import os
import time
from rasterio.windows import Window

# from cos_backend import COSBackend


def obtain_meta(chunk, splits):
    with rasterio.open(chunk) as src:
        profile = src.profile
        profile.update(width=profile['width'] * splits)
        profile.update(height=profile['height'] * splits)
    return profile


def gather_blocks(tiles, profile):
    with rasterio.open("output", "w", **profile) as dest:
        for tile in tiles:
            tileb, (block_x, block_y) = tile
            print("Updating chunk ({}, {})".format(block_x, block_y))
            with rasterio.open(tileb) as src:
                curr_window = Window(round(src.width * int(block_x) % src.width),
                                     round(src.height * int(block_y) % src.height),
                                     src.width,
                                     src.height)
                content = src.read(1)
                dest.write(content, 1, window=curr_window)
    return 'output'


def main(args):
    start_time = time.time()
    parameters = SimpleNamespace(**args['parameters'])
    # cos = COSBackend(aws_access_key_id=args['cos']['aws_access_key_id'],
    #                  aws_secret_access_key=args['cos']['aws_secret_access_key'],
    #                  endpoint_url=args['cos']['private_endpoint'])

    keys = cos.list_keys_prefix(bucket=parameters.BUCKET, prefix='tmp/{}/{}'.format(args['type'], args['tile']))

    chunk = cos.get_object(key=keys[0], bucket=parameters.BUCKET)
    profile = obtain_meta(chunk, parameters.SPLITS)

    tiles = ((cos.get_object(bucket=parameters.BUCKET, key=key), tuple(os.path.basename(key)[:3].split('_')))
             for key in keys)
    out = gather_blocks(tiles, profile)

    result_key = '/'.join(['tmp', args['type'], args['tile'], 'merged.tif'])
    # cos.upload_file(filename=out, bucket=parameters.BUCKET, key=result_key)
    end_time = time.time()
    return {'result': result_key, 'start_time': start_time, 'end_time': end_time}
