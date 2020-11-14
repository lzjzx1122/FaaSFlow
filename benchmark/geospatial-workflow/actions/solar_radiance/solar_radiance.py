import os
import re
import math
import shutil
import numpy as np
import rasterio
import sys
import time

sys.path.append('/usr/lib/grass76/etc/python')
os.environ['GISBASE'] = "/usr/lib/grass76/"
os.environ['GRASSBIN'] = "grass76"

import grass.script as gscript

# from cos_backend import COSBackend

from types import SimpleNamespace
from rasterio.windows import Window
from grass_session import Session
from grass.pygrass.modules.shortcuts import general as g
from grass.pygrass.modules.shortcuts import raster as r

os.environ['GRASSBIN'] = 'grass76'


def compute_solar_irradiation(inputFile, outputFile, day_of_year, crs='32630'):
    # Define grass working set
    GRASS_GISDB = 'grassdata'
    GRASS_LOCATION = 'GEOPROCESSING'
    GRASS_MAPSET = 'PERMANENT'
    GRASS_ELEVATIONS_FILENAME = 'ELEVATIONS'

    os.environ.update(dict(GRASS_COMPRESS_NULLS='1'))

    # Clean previously processed data
    if os.path.isdir(GRASS_GISDB):
        shutil.rmtree(GRASS_GISDB)
    with Session(gisdb=GRASS_GISDB, location=GRASS_LOCATION, mapset=GRASS_MAPSET, create_opts='EPSG:32630') as ses:

        # Set project projection to match elevation raster projection
        g.proj(epsg=crs, flags='c')

        # Load raster file into working directory
        r.import_(input=inputFile,
                  output=GRASS_ELEVATIONS_FILENAME,
                  flags='o')

        # Set project region to match raster region
        g.region(raster=GRASS_ELEVATIONS_FILENAME, flags='s')
        # Calculate solar irradiation
        gscript.run_command('r.slope.aspect', elevation=GRASS_ELEVATIONS_FILENAME, slope='slope', aspect='aspect')
        gscript.run_command('r.sun', elevation=GRASS_ELEVATIONS_FILENAME, slope='slope', aspect='aspect',
                            beam_rad='beam', step=1, day=day_of_year)

        # Get extraterrestrial irradiation from history metadata
        regex = re.compile(r'\d+\.\d+')
        output = gscript.read_command("r.info", flags="h", map=["beam"])
        splits = str(output).split('\n')
        line = next(filter(lambda line: 'Extraterrestrial' in line, splits))
        extraterrestrial_irradiance = float(regex.search(line)[0])

        # Export generated results into a GeoTiff file
        if os.path.isfile(outputFile):
            os.remove(outputFile)

        r.out_gdal(input='beam', output=outputFile)
        return extraterrestrial_irradiance


def map_interpolation(mdt, day_of_year, block_x, block_y, splits):

    with rasterio.open(mdt) as src:
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
        with rasterio.open('input', "w", **profile) as dest:
            dest.write(src.read(window=window))
        # Stores global irradiation at "output", it also returns extraterrestrial irradiation
        extraterrestrial_irradiation = compute_solar_irradiation('input', 'output', day_of_year)
        # Create and store a raster with extraterrestrial_irradiation
        with rasterio.open('extr', "w", **profile) as dest:
            data = np.full((height, width), extraterrestrial_irradiation, dtype='float32')
            dest.write(data, 1)

    return 'extr'


def main(args):
    start_time = time.time()
    args.update(args['chunk'])
    parameters = SimpleNamespace(**args['parameters'])
    # cos = COSBackend(aws_access_key_id=args['cos']['aws_access_key_id'],
    #                  aws_secret_access_key=args['cos']['aws_secret_access_key'],
    #                  endpoint_url=args['cos']['private_endpoint'])
    mdt_key = args['mdt_key']
    # mdt = cos.get_object(key=mdt_key, bucket=parameters.BUCKET)
    mdt = mdt_key

    filename = map_interpolation(mdt, parameters.DAY_OF_YEAR, args['block_x'], args['block_y'], parameters.SPLITS)

    # result_key = '/'.join(['tmp', 'EXTRAD',
    #                        os.path.basename(mdt_key).rsplit('.')[0],
    #                        str(args['block_x']) + '_' + str(args['block_y']) + '.tif'])
    # cos.upload_file(filename=filename, bucket=parameters.BUCKET, key=result_key)

    # result_key = '/'.join(['tmp', 'RADIANCE',
    #                        os.path.basename(mdt_key).rsplit('.')[0],
    #                        str(args['block_x']) + '_' + str(args['block_y']) + '.tif'])
    # cos.upload_file(filename='output', bucket=parameters.BUCKET, key=result_key)
    end_time = time.time()
    return {'result': result_key, 'start_time': start_time, 'end_time': end_time}
