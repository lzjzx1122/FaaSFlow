from shapely.geometry import Point, MultiPoint
from shapely.ops import nearest_points
import pandas as pd
import requests
import math
import time
from types import SimpleNamespace

# from cos_backend import COSBackend


def guess_nearest(x, y, field, stations):
    """
    Compute field value at a given x,y point by getting the value of the closest station
    """
    stations_of_interest = stations[(stations[field] != '-') & ((stations['X'] != x) | (stations['Y'] != y))]
    points = MultiPoint(stations_of_interest.apply(lambda row: Point(row['X'], row['Y']), axis=1).array)
    nearest = nearest_points(Point(x, y), points)[1]
    # val = stations_of_interest[(stations_of_interest['X'] == nearest.x) &
    #                            (stations_of_interest['Y'] == nearest.y)]

    return stations_of_interest[(stations_of_interest['X'] == nearest.x) &
                                (stations_of_interest['Y'] == nearest.y)][field].iloc[0]


def main(args):
    start_time = time.time()
    parameters = SimpleNamespace(**args['parameters'])
    # cos = COSBackend(aws_access_key_id=args['cos']['aws_access_key_id'],
    #                  aws_secret_access_key=args['cos']['aws_secret_access_key'],
    #                  endpoint_url=args['cos']['private_endpoint'])
    # url = args['url']
    # siam_data = requests.get(url)
    # with open('siam_data.csv', 'wb') as siam_file:
    #     siam_file.write(siam_data.content)

    # cos.download_file(bucket=parameters.BUCKET, key='siam_locations.csv', filename='siam_locations.csv')

    columns = {
        'Estación': 'COD',
        'Tmed <br> (ºC)': 'temp',
        'Hrmed <br> (%)': 'hr',
        'Vvmed <br> (m/seg)': 'v',
        'Eti.': 'dir',
        'Radmed <br> (w/m2)': 'rad',
        'Dvmed <br>  (º)': 'dir_deg'
    }

    siam_data = pd.read_csv('siam_data.csv', encoding='iso-8859-1', sep=';', decimal=',', thousands='.',
                            na_values='-')
    siam_data = siam_data[columns.keys()].rename(columns=columns)
    siam_locations = pd.read_csv('siam_locations.csv', encoding='iso-8859-1', sep=';', decimal=',', thousands='.')
    siam = pd.merge(siam_locations, siam_data, on='COD')
    siam['tdet'] = siam['temp'] + parameters.r * (parameters.zdet - siam['Cota'].to_numpy())
    siam = siam[['X', 'Y', 'Cota', 'temp', 'hr', 'tdet', 'v'] + list(columns.values())]
    # Guess wind direction of undefined values
    siam['dir_deg'] = siam.apply(lambda row: row['dir_deg']
        if not math.isnan(row['dir_deg'])
        else guess_nearest(row['X'], row['Y'], 'dir_deg', siam), axis=1)
    # Guess radiation of undefined values
    siam['rad'] = siam.apply(lambda row: row['rad']
        if not math.isnan(row['rad'])
        else guess_nearest(row['X'], row['Y'], 'rad', siam), axis=1)
    # TODO: currently write to local file
    siam.to_csv('siam_out.csv', index=False)

    # cos.upload_file(filename='siam_out.csv',
    #                 bucket=parameters.BUCKET,
    #                 key='siam_out.csv')
    end_time = time.time()
    return {'result': 'siam_out.csv', 'start_time': start_time, 'end_time': end_time}
