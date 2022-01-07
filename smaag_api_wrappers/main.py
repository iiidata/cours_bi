# This is a sample Python script.

# Press Maj+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import datetime
import glob
import json
import multiprocessing
import os
import sys

import pandas as pd
import requests
import logging.config
from logging import StreamHandler
from logging.handlers import TimedRotatingFileHandler

from enquete_parser import EnqueteParser

############### LOGGING file #############
logger = logging.getLogger()
LOG_LEVEL = logging.INFO
logger.setLevel(LOG_LEVEL)
LOG_FORMAT = '%(asctime)s :: %(levelname)s :: %(message)s'
LOG_DATE_FORMAT = '%d/%m/%Y %H:%M:%S'
formatter = logging.Formatter(LOG_FORMAT)
basedir = os.path.abspath(os.path.join(os.path.dirname(__file__)))
LOG_DIRECTORY = os.path.join(basedir, 'logs')
os.makedirs(LOG_DIRECTORY, exist_ok=True)
file_handler = TimedRotatingFileHandler(filename=os.path.join(LOG_DIRECTORY,'wrapper.log'), when='h')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
LOG_LEVEL = logging.DEBUG
logger.setLevel(LOG_LEVEL)
logger.addHandler(logging.StreamHandler(stream=sys.stdout))

API_SERVER = "https://data.mobilites-m.fr"

SMMAG_ENDPOINTS = {
    'lines':'/api/routers/default/index/routes',
    'clusters':'/api/routers/default/index/routes/{line_id}/clusters',
    'stops':'/api/routers/default/index/routes/{line_id}/stops',
    'cities':'/api/city/json',
    'lineSchedules':'/api/ficheHoraires/json?route={line_id}',
    'occupancy':'/api/stops/{stop_id}/occupancy/json',
    'cluster_stoptimes':'/api/routers/default/index/clusters/{cluster_id}/stoptimes'
}

PATH_FILE = 'data'
basedir = os.path.abspath(os.path.join(os.path.dirname(__file__)))

def call_api(endpoint, **kwargs):

    url = f"{API_SERVER}{endpoint}"
    params = dict()
    if kwargs.get('headers'):
        params['headers'] = kwargs.get('headers')

    if kwargs.get('payload'):
        params['payload'] = kwargs.get('payload')
    try:
        response = requests.get(url, **params )
        if response.status_code != 200:
            raise ValueError(f'Unable to get data from url {url} : error {response.status_code}')
        return json.loads(response.content)
    except ConnectionError as e:
        raise ValueError(f'Unable to get data from url {url} : error {e}')


def get_lines():
    """
    Get all SMAAG lines
    :return: dataframe
    """
    content = call_api(SMMAG_ENDPOINTS.get('lines'))
    df = pd.DataFrame()
    df = df.from_records(content)
    df = df.reset_index(drop=True)
    return df


def get_clusters(lines):
    df = pd.DataFrame()
    for line in lines:
        content = call_api(SMMAG_ENDPOINTS.get('clusters').format(line_id=line))
        df_line_clusters = pd.DataFrame().from_records(content)
        df_line_clusters['line_id'] = line
        df_line_clusters['way_order'] = df_line_clusters.index
        df = df.append(df_line_clusters)
    return df


def get_stops(lines):
    df = pd.DataFrame()
    for line in lines:
        content = call_api(SMMAG_ENDPOINTS.get('stops').format(line_id=line))
        df_line_stops = pd.DataFrame().from_records(content)
        df_line_stops['line_id'] = line
        df_line_stops['way_order'] = df_line_stops.index
        df = df.append(df_line_stops)
    return df


def get_cities():
    content = call_api(SMMAG_ENDPOINTS.get('cities'))
    df = pd.DataFrame()
    df = df.from_records(content)
    df = df.reset_index(drop=True)
    return df


def get_schedules(lines):
    df = pd.DataFrame()
    for line in lines:
        content = call_api(SMMAG_ENDPOINTS.get('lineSchedules').format(line_id=line))
        df_line_schedules = pd.DataFrame().from_records(content)
        df_line_schedules['line_id'] = line
        df = df.append(df_line_schedules)
    return df


def get_occupancy(stops):
    df = pd.DataFrame()
    for stop in stops:
        content = call_api(SMMAG_ENDPOINTS.get('occupancy').format(stop_id=stop))
        timeslots = content.get('timeSlots')
        if content.get('occupancy'):
            directions:dict = content.get('occupancy').get('routeDirection')
            for direction, occupancy in directions.items():
                df_stop_occupancy = pd.DataFrame(list(zip(timeslots, occupancy)), columns =['timeSlot', 'occupancy'])
                df_stop_occupancy['routeDirection'] = direction
                df_stop_occupancy['stop_id'] = stop
                df = df.append(df_stop_occupancy)
    return df


def get_referentials():

    lines_file = 'smmag_lines.csv'
    line_clusters_file = 'smmag_line_clusters.csv'
    line_stops_file = 'smmag_line_stops.csv'
    line_schedules_file = 'smmag_line_schedules.csv'
    stop_occupancy_file = 'smmag_stop_occupancy.csv'
    cities_file = 'cities.csv'

    if os.path.exists(os.path.join(basedir, PATH_FILE, lines_file) ):
        df_lines = pd.read_csv(lines_file)
    else:
        df_lines = get_lines()
        df_lines.to_csv(lines_file, index=False)

    df_clusters_per_line = get_clusters(df_lines['id'].tolist())
    df_clusters_per_line.to_csv(line_clusters_file, index=False)

    df_stops_per_line = get_stops(df_lines['id'].tolist())
    df_stops_per_line.to_csv(line_stops_file, index=False)
    #
    df_cities = get_cities()
    df_cities.to_csv(cities_file, index=False)

    # df_line_schedules = get_schedules(df_lines['id'].tolist())
    # df_line_schedules.to_csv(line_schedules_file, index=False)

    if os.path.exists(os.path.join(basedir, PATH_FILE, line_stops_file) ):
        df_linestops = pd.read_csv(line_stops_file)

    linestops = df_linestops['id'].drop_duplicates().tolist()
    df_stop_occupancy = get_occupancy(linestops)
    df_stop_occupancy.to_csv(stop_occupancy_file, index=False)


def get_semitag_stop_times():
    path = os.path.join(basedir, PATH_FILE, 'smmag_line_clusters.csv')
    if os.path.exists(path):
        df_lineclusters = pd.read_csv(path)
        ## limit at SEMA
        df_lineclusters = df_lineclusters[df_lineclusters['code'].str.contains('SEM:', na=True)]
    lineclusters = df_lineclusters['code'].drop_duplicates().tolist()
    headers = {
        'origin': 'campus_num'
    }

    data = []
    for clust in lineclusters:
        call_datetime = datetime.datetime.now()
        # logger.debug(f'call cluster : {clust}')
        try:

            content = call_api(SMMAG_ENDPOINTS.get('cluster_stoptimes').format(cluster_id=clust), headers=headers)
            if len(content) > 0:
                for route in content:
                    pattern = route.get('pattern')
                    pattern_id = pattern.get('id')
                    pattern_desc = pattern.get('desc')
                    pattern_dir = pattern.get('dir')
                    pattern_last_stop = pattern.get('lastStop')
                    times = route.get('times')
                    for time in times:
                        stop_id = time.get('stopId')
                        scheduled_arrival = time.get('scheduledArrival')
                        scheduled_departure = time.get('scheduledDeparture')
                        realtime_arrival = time.get('realtimeArrival')
                        realtime_departure = time.get('realtimeDeparture')
                        arrival_delay = time.get('arrivalDelay')
                        departure_delay = time.get('departureDelay')
                        timepoint = time.get('timepoint')
                        realtime = time.get('realtime')
                        realtime_state = time.get('realtimeState')
                        service_day = time.get('serviceDay')
                        trip_id = time.get('tripId')
                        headsign = time.get('headsign')

                        row = {
                            'call_timestamp':call_datetime,
                            'cluster_id':clust,
                            'pattern_id':pattern_id,
                            'pattern_desc':pattern_desc,
                            'pattern_dir':pattern_dir,
                            'pattern_last_stop': pattern_last_stop,
                            'stop_id': stop_id,
                            'scheduled_arrival': scheduled_arrival,
                            'scheduled_departure': scheduled_departure,
                            'realtime_arrival': realtime_arrival,
                            'realtime_departure': realtime_departure,
                            'arrival_delay': arrival_delay,
                            'departure_delay': departure_delay,
                            'timepoint': timepoint,
                            'realtime': realtime,
                            'realtime_state': realtime_state,
                            'service_day': service_day,
                            'trip_id': trip_id,
                            'headsign': headsign
                        }
                        data.append(row)
        except Exception as e:
            logger.info(e)
    df = pd.DataFrame(data)
    path = os.path.join(basedir, PATH_FILE, 'smmag_line_clusters.csv')
    df.to_csv(path, index=False, mode='a')


def parse_enquetes():

    # enquetes_dir = 'enquetes/'
    enquetes_dir = ''
    dest = os.path.join(basedir, PATH_FILE ,'temp_files')
    d1 = os.path.join(dest, 'updown_per_cluster_inout')
    d2 = os.path.join(dest, 'updown_per_cluster_and_semline')
    d3 = os.path.join(dest, 'updown_per_cluster_and_mode')

    os.makedirs(dest, exist_ok=True)
    os.makedirs(d1, exist_ok=True)
    os.makedirs(d2, exist_ok=True)
    os.makedirs(d3, exist_ok=True)

    p = multiprocessing.Pool()
    for filename in os.listdir(os.path.join(basedir, PATH_FILE, enquetes_dir)):
        # launch a process for each file (ish).
        # The result will be approximately one process per CPU core available.
        f = os.path.join(basedir, enquetes_dir, filename)
        p.apply_async(process_file_enquete, [f,dest])

    p.close()
    p.join()  # Wait for all child processes to close.

    all_filenames = [i for i in glob.glob(os.path.join(basedir, dest,'updown_per_cluster_inout','*.csv'))]
    combined_csv = pd.concat([pd.read_csv(f) for f in all_filenames])
    combined_csv.to_csv(os.path.join(basedir, "updown_per_cluster_inout.csv"), index=False, encoding='utf-8')

    all_filenames = [i for i in glob.glob(os.path.join(basedir, dest, 'updown_per_cluster_and_semline','*.csv'))]
    combined_csv = pd.concat([pd.read_csv(f) for f in all_filenames])
    combined_csv.to_csv(os.path.join(basedir, "updown_per_cluster_and_semline.csv"), index=False, encoding='utf-8')

    all_filenames = [i for i in glob.glob(os.path.join(basedir, dest, 'updown_per_cluster_and_mode','*.csv'))]
    combined_csv = pd.concat([pd.read_csv(f) for f in all_filenames])
    combined_csv.to_csv(os.path.join(basedir, "updown_per_cluster_and_mode.csv"), index=False, encoding='utf-8')


def process_file_enquete(f,dest):
    logger.info(f"-------------------{f}----------------------")
    filename = os.path.basename(f).split('.')[0]
    ep = EnqueteParser(f)
    df_updown_per_cluster, df_updown_per_cluster_and_semline, df_updown_per_cluster_and_mode = ep.parse()
    f1 = os.path.join(basedir, dest,'updown_per_cluster_inout',f'{filename}.csv')
    f2 = os.path.join(basedir, dest, 'updown_per_cluster_and_semline', f'{filename}.csv')
    f3 = os.path.join(basedir, dest, 'updown_per_cluster_and_mode', f'{filename}.csv')
    df_updown_per_cluster.to_csv(f1, index=False, mode='w')
    df_updown_per_cluster_and_semline.to_csv(f2, index=False, mode='w')
    df_updown_per_cluster_and_mode.to_csv(f3, index=False, mode='w')

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    logger.info('start collect stop time')
    start = datetime.datetime.now()
    get_semitag_stop_times()
    end = datetime.datetime.now()
    logger.info(f'finish collect stop time : {end}')
    logger.info('start pase enquetes')
    start = datetime.datetime.now()
    parse_enquetes()
    end = datetime.datetime.now()
    logger.info(f'finish parse stop time : {end}')


# See PyCharm help at https://www.jetbrains.com/help/pycharm/
