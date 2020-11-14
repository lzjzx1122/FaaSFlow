import yaml
import os

def add_next(first_nodes, next_nodes):
    names = [n['name'] for n in next_nodes]
    for n in first_nodes:
        if 'next' not in n:
            n['next'] = []
        if type(n['next']) is str:
            n['next'] = [n['next']]
        n['next'] += names
    return first_nodes

params = {
    'AREA_OF_INFLUENCE': 4000,
    'SPLITS': 5,
    'r': -0.0056,
    'zdet': 2000,
    'DAY_OF_YEAR': 50
}

workflow = None
with open('workflow_template.yaml', 'r') as f:
    workflow = yaml.safe_load(f)

asc_file = ['PNOA_MDT05_ETRS89_HU30_0933_LID.asc']
tiles = [os.path.splitext(os.path.basename(tile))[0] for tile in asc_file]
tiffs = ['{}.tif'.format(tile) for tile in tiles]
iter_data = [{'block_x': x, 'block_y': y, 'mdt_key': key}
             for x in range(params['SPLITS'])
             for y in range(params['SPLITS'])
             for key in tiffs]

start_node = {
    'name': 'start_node',
    'type': 'dummy',
    'next': 'get_stations'
}

get_stations = {
    'name': 'get_stations',
    'type': 'function',
    'source': 'get_stations',
    'next': 'wait_for_data'
}

asc_to_geotiff = []
for i, filename in enumerate(asc_file):
    asc_to_geotiff.append({
        'name': f'asc_to_geotiff_{i}',
        'type': 'function',
        'source': 'asc_to_geotiff',
        'parameters': {
            'mdt_key': filename
        },
        'next': 'wait_for_data'
    })

wait_for_data = {
    'name': 'wait_for_data',
    'type': 'dummy'
}

compute_solar_radiance = []
for chunk in iter_data:
    compute_solar_radiance.append({
        'name': f'compute_solar_radiance_{chunk["block_x"]}_{chunk["block_y"]}_{chunk["mdt_key"]}',
        'type': 'function',
        'source': 'solar_radiance',
        'parameters': {
            'chunk': chunk,
            'parameters': params
        }
    })

merge_global_radiance = []
for tile in tiles:
    merge_global_radiance.append({
        'name': f'merge_global_radiance_{tile}',
        'type': 'function',
        'source': 'gather_blocks',
        'parameters': {
            'type': 'RADIANCE',
            'parameters': params,
            'tile': tile
        }
    })

merge_extraterrestrial_radiance = []
for tile in tiles:
    merge_extraterrestrial_radiance.append({
        'name': f'merge_extraterrestrial_radiance_{tile}',
        'type': 'function',
        'source': 'gather_blocks',
        'parameters': {
            'type': 'EXTRAD',
            'parameters': params,
            'tile': tile
        }
    })

compute_temperature_interpolation = []
for chunk in iter_data:
    compute_temperature_interpolation.append({
        'name': f'interpolate_temperature_{chunk["block_x"]}_{chunk["block_y"]}_{chunk["mdt_key"]}',
        'type': 'function',
        'source': 'interpolate_temperature',
        'parameters': {
            'chunk': chunk,
            'parameters': params
        }
    })

merge_temperature_interpolation = []
for tile in tiles:
    merge_temperature_interpolation.append({
        'name': f'merge_temperature_interpolation_{tile}',
        'type': 'function',
        'source': 'gather_blocks',
        'parameters': {
            'type': 'TEMPERATURE',
            'parameters': params,
            'tile': tile
        }
    })

compute_wind_interpolation = []
for chunk in iter_data:
    compute_wind_interpolation.append({
        'name': f'interpolate_wind_{chunk["block_x"]}_{chunk["block_y"]}_{chunk["mdt_key"]}',
        'type': 'function',
        'source': 'interpolate_wind',
        'parameters': {
            'chunk': chunk,
            'parameters': params
        }
    })

merge_wind_interpolation = []
for tile in tiles:
    merge_wind_interpolation.append({
        'name': f'merge_wind_interpolation_{tile}',
        'type': 'function',
        'source': 'gather_blocks',
        'parameters': {
            'type': 'WIND',
            'parameters': params,
            'tile': tile
        }
    })

compute_humidity_interpolation = []
for chunk in iter_data:
    compute_humidity_interpolation.append({
        'name': f'interpolate_humidity_{chunk["block_x"]}_{chunk["block_y"]}_{chunk["mdt_key"]}',
        'type': 'function',
        'source': 'interpolate_humidity',
        'parameters': {
            'chunk': chunk,
            'parameters': params
        }
    })

merge_humidity_interpolation = []
for tile in tiles:
    merge_humidity_interpolation.append({
        'name': f'merge_humidity_interpolation_{tile}',
        'type': 'function',
        'source': 'gather_blocks',
        'parameters': {
            'type': 'HUMIDITY',
            'parameters': params,
            'tile': tile
        }
    })

combine_calculations = []
for tile in tiles:
    combine_calculations.append({
        'name': f'combine_calculations_{tile}',
        'type': 'function',
        'source': 'combine_calculations',
        'parameters': {
            'tile': tile
        },
        'next': 'end_node'
    })

end_node = {
    'name': 'end_node',
    'type': 'dummy'
}

(start_node,) = add_next([start_node], asc_to_geotiff)
(wait_for_data,) = add_next([wait_for_data], compute_solar_radiance + compute_humidity_interpolation + compute_temperature_interpolation + compute_wind_interpolation)
compute_solar_radiance = add_next(compute_solar_radiance, merge_global_radiance + merge_extraterrestrial_radiance)
compute_humidity_interpolation = add_next(compute_humidity_interpolation, merge_humidity_interpolation)
compute_temperature_interpolation = add_next(compute_temperature_interpolation, merge_temperature_interpolation)
compute_wind_interpolation = add_next(compute_wind_interpolation, merge_wind_interpolation)
merge_global_radiance = add_next(merge_global_radiance, combine_calculations)
merge_extraterrestrial_radiance = add_next(merge_extraterrestrial_radiance, combine_calculations)
merge_humidity_interpolation = add_next(merge_humidity_interpolation, combine_calculations)
merge_temperature_interpolation = add_next(merge_temperature_interpolation, combine_calculations)
merge_wind_interpolation = add_next(merge_wind_interpolation, combine_calculations)

nodes = [start_node, get_stations, wait_for_data, end_node]
nodes += compute_solar_radiance + merge_global_radiance + merge_extraterrestrial_radiance
nodes += compute_humidity_interpolation + merge_humidity_interpolation
nodes += compute_temperature_interpolation + merge_temperature_interpolation
nodes += compute_wind_interpolation + merge_wind_interpolation
nodes += combine_calculations
workflow['main']['nodes'] = nodes

class NoAliasDumper(yaml.Dumper):
    def ignore_aliases(self, data):
        return True

with open('workflow_geospatial.yaml', 'w') as f:
    yaml.dump(workflow, f, Dumper=NoAliasDumper)