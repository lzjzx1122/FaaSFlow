import rasterio
import os
import time
from types import SimpleNamespace

# from cos_backend import COSBackend


def main(args):
    start_time = time.time()
    # parameters = SimpleNamespace(**args['parameters'])
    mdt_key = args['mdt_key']
    mdt_filename = os.path.basename(mdt_key)
    # cos = COSBackend(aws_access_key_id=args['cos']['aws_access_key_id'],
    #                  aws_secret_access_key=args['cos']['aws_secret_access_key'],
    #                  endpoint_url=args['cos']['private_endpoint'])
    # cos.download_file(parameters.BUCKET, mdt_key, mdt_filename)

    tiff_file = os.path.splitext(mdt_filename)[0] + '.tif'
    with rasterio.open(mdt_filename) as src:
        profile = src.profile
        # Cloud optimized GeoTiff parameters (No hace falta rio_cogeo)
        profile.update(driver='GTiff')
        profile.update(blockxsize=256)
        profile.update(blockysize=256)
        profile.update(tiled=True)
        profile.update(compress='deflate')
        profile.update(interleave='band')
        # TODO: currently write to local file
        with rasterio.open(tiff_file, "w", **profile) as dest:
            dest.write(src.read())

        # cos.upload_file(filename=tiff_file, bucket=parameters.BUCKET, key='tiff/{}'.format(tiff_file))
    end_time = time.time()

    return {'result': tiff_file, 'start_time': start_time, 'end_time': end_time}
