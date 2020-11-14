import os
import pprint

from triggerflow.dags import DAG
from triggerflow.dags.operators import IBMCloudFunctionsCallAsyncOperator, IBMCloudFunctionsMapOperator, DummyOperator


water_consumption = DAG(dag_id='water_consumption')

# INPUT PARAMETERS
params = {
    'AREA_OF_INFLUENCE': 4000,
    'BUCKET': os.environ['BUCKET'],
    'SPLITS': 5,
    'r': -0.0056,
    'zdet': 2000,
    'DAY_OF_YEAR': 50
}

cos = {
    'private_endpoint': 'https://s3.private.us-south.cloud-object-storage.appdomain.cloud',
    'public_endpoint': 'https://s3.us-south.cloud-object-storage.appdomain.cloud',
    'aws_access_key_id': os.environ['AWS_ACCESS_KEY_ID'],
    'aws_secret_access_key': os.environ['AWS_SECRET_ACCESS_KEY']
}

url = 'http://siam.imida.es/apex/f?p=101:47:493289053024037:CSV::::'
# keys = ['PNOA_MDT05_ETRS89_HU30_0913_LID.asc', 'PNOA_MDT05_ETRS89_HU30_0952_LID.asc',
#         'PNOA_MDT05_ETRS89_HU30_0955_LID.asc', 'PNOA_MDT05_ETRS89_HU30_0977_LID.asc']
keys = ['PNOA_MDT05_ETRS89_HU30_0933_LID.asc']
tiles = [os.path.splitext(os.path.basename(tile))[0] for tile in keys]
print("Tiles:")
pprint.pprint(tiles)
tiffs = ['tiff/{}.tif'.format(tile) for tile in tiles]

# TASKS

get_stations = IBMCloudFunctionsCallAsyncOperator(
    task_id='get_stations',
    function_name='get_stations',
    function_package='geospatial-dag',
    invoke_kwargs={'cos': cos, 'parameters': params, 'url': url},
    dag=water_consumption,
)

asc_to_geotiff = IBMCloudFunctionsMapOperator(
    task_id='asc_to_geotiff',
    function_name='asc_to_geotiff',
    function_package='geospatial-dag',
    invoke_kwargs={'cos': cos, 'parameters': params},
    iter_data={'mdt_key': keys},
    dag=water_consumption,
)

wait_for_data = DummyOperator(
    task_id='wait_for_data',
    dag=water_consumption
)

iter_data = [{'block_x': x, 'block_y': y, 'mdt_key': key}
             for x in range(params['SPLITS'])
             for y in range(params['SPLITS'])
             for key in tiffs]

compute_solar_radiance = IBMCloudFunctionsMapOperator(
    task_id='compute_solar_radiance',
    function_name='solar_radiance',
    function_package='geospatial-dag',
    invoke_kwargs={'cos': cos, 'parameters': params},
    iter_data={'chunk': iter_data},
    dag=water_consumption,
)

merge_global_radiance = IBMCloudFunctionsMapOperator(
    task_id='merge_global_radiance',
    function_name='gather_blocks',
    function_package='geospatial-dag',
    invoke_kwargs={'cos': cos, 'parameters': params, 'type': 'RADIANCE'},
    iter_data={'tile': tiles},
    dag=water_consumption,
)

merge_extraterrestrial_radiance = IBMCloudFunctionsMapOperator(
    task_id='merge_extraterrestrial_radiance',
    function_name='gather_blocks',
    function_package='geospatial-dag',
    invoke_kwargs={'cos': cos, 'parameters': params, 'type': 'EXTRAD'},
    iter_data={'tile': tiles},
    dag=water_consumption,
)

compute_temperature_interpolation = IBMCloudFunctionsMapOperator(
    task_id='interpolate_temperature',
    function_name='interpolate_temperature',
    function_package='geospatial-dag',
    invoke_kwargs={'cos': cos, 'parameters': params},
    iter_data={'chunk': iter_data},
    dag=water_consumption,
)

merge_temperature_interpolation = IBMCloudFunctionsMapOperator(
    task_id='merge_temperature_interpolation',
    function_name='gather_blocks',
    function_package='geospatial-dag',
    invoke_kwargs={'cos': cos, 'parameters': params, 'type': 'TEMPERATURE'},
    iter_data={'tile': tiles},
    dag=water_consumption,
)

compute_wind_interpolation = IBMCloudFunctionsMapOperator(
    task_id='interpolate_wind',
    function_name='interpolate_wind',
    function_package='geospatial-dag',
    invoke_kwargs={'cos': cos, 'parameters': params},
    iter_data={'chunk': iter_data},
    dag=water_consumption,
)

merge_wind_interpolation = IBMCloudFunctionsMapOperator(
    task_id='merge_wind_interpolation',
    function_name='gather_blocks',
    function_package='geospatial-dag',
    invoke_kwargs={'cos': cos, 'parameters': params, 'type': 'WIND'},
    iter_data={'tile': tiles},
    dag=water_consumption,
)

compute_humidity_interpolation = IBMCloudFunctionsMapOperator(
    task_id='interpolate_humidity',
    function_name='interpolate_humidity',
    function_package='geospatial-dag',
    invoke_kwargs={'cos': cos, 'parameters': params},
    iter_data={'chunk': iter_data},
    dag=water_consumption,
)

merge_humidity_interpolation = IBMCloudFunctionsMapOperator(
    task_id='merge_humidity_interpolation',
    function_name='gather_blocks',
    function_package='geospatial-dag',
    invoke_kwargs={'cos': cos, 'parameters': params, 'type': 'HUMIDITY'},
    iter_data={'tile': tiles},
    dag=water_consumption,
)

combine_calculations = IBMCloudFunctionsMapOperator(
    task_id='combine_calculations',
    function_name='combine_calculations',
    function_package='geospatial-dag',
    invoke_kwargs={'cos': cos, 'parameters': params},
    iter_data={'tile': tiles},
    dag=water_consumption,
)

# SET TASKS DEPENDENCIES

wait_for_data << [get_stations, asc_to_geotiff]

wait_for_data >> [compute_solar_radiance,
                  compute_humidity_interpolation,
                  compute_temperature_interpolation,
                  compute_wind_interpolation]

compute_solar_radiance >> [merge_global_radiance, merge_extraterrestrial_radiance]
compute_wind_interpolation >> merge_wind_interpolation
compute_humidity_interpolation >> merge_humidity_interpolation
compute_temperature_interpolation >> merge_temperature_interpolation

combine_calculations << [merge_global_radiance,
                         merge_extraterrestrial_radiance,
                         merge_wind_interpolation,
                         merge_humidity_interpolation,
                         merge_temperature_interpolation]


# water_consumption.save()

