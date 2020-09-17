import csv
import os
import requests
import datetime

import common

RAW_DATA_DIR = os.path.join(os.getcwd(), 'src', 'raw_coop_data')


def str_date_to_datetime(str_date):
    x = str_date.split(' ')[0].split('-')
    return datetime.datetime(int(x[0]), int(x[1]), int(x[2]))

def get_stations():
    stations = []

    with open(os.path.join(os.getcwd(), 'src', 'coop_stations_to_use.csv'), 'r') as csv_file:
        coop_reader = csv.reader(csv_file)
        header = next(coop_reader)
        for row in coop_reader:
            if row[6] == 'True':
                in_basins = True
            else:
                in_basins = False
            if row[7] == 'True':
                break_with_basins = True
            else:
                break_with_basins = False
            stations.append(common.Station(row[0], row[1], str_date_to_datetime(row[2]),
                                           str_date_to_datetime(row[3]), row[4], row[5],
                                           in_basins, break_with_basins))


    return stations

def get_data(coop_stations):
    base_url = common.CHPD_BASE_URL + 'access/'

    # for station in coop_stations:
    station = coop_stations
    # print(station.start_date, station.end_date)]
    #TODO might not need one of those 0's
    the_url = base_url + 'USC00' + station.station_id + '.csv'
    # print(the_url)

    r = requests.get(the_url)
    print(r.content)
    print(r.status_code)

    with open(os.path.join(RAW_DATA_DIR, station.station_id + '.csv'), 'wb') as file:
        file.write(r.content)

def process_data(station, basins, start_date, end_date):
    with open(os.path.join(RAW_DATA_DIR, station.station_id + '.csv'), 'rb') as file:
        data = file.readlines()

    header = data.pop(0)
    # print(header)

    debug_year_precip = 0
    missing = 0
    partial = 0

    for item in data:

        split_item = item.split(b',')
        raw_date = split_item[4].decode().split('-')
        actual_date = datetime.datetime(int(raw_date[0]), int(raw_date[1]), int(raw_date[2]))

        if actual_date.year == 2006:
            the_value = item.decode().strip('\n').split(',')
            # TODO check flags

            precip_values = the_value[6:-5:5]

            # check last records
            # print(the_value[-5])
            assert the_value[-4] == ' '
            if the_value[-3] != ' ':  # 'P' is for partial
                partial += 1
            assert the_value[-2] == ' '
            assert the_value[-1] == 'C'

            for item in precip_values:
                # print(item)
                if item == '-9999':
                    missing += 1
                    item = 0
                    # print(item)

            float_precip = [int(x) for x in precip_values]  # -9999?

            for item in float_precip:
                if item < -1:
                    pass
                else:
                    debug_year_precip += item

            # debug_year_precip += sum(float_precip)

    print(debug_year_precip)
    print(missing)
    print(partial)



if __name__  == '__main__':
    coop_stations_to_use = get_stations()
    split_basins_data = common.read_basins_file()
    basins_stations = common.make_basins_stations(split_basins_data)
    # print(basins_stations)

    # get_data(coop_stations_to_use[2]) # 2 -> ALBERTA
    # Alberta is "most" typical -- BASINS goes thru 12/31/2006 and COOP is current

    which_station_id = '332974'  # in BASINS and current
    # which_station_id = '106174' # in BASINS and not current
    which_station_id = '358717' # not in BASINS and current
    which_station_id = '214546'
    which_station_id = '018178'  # example where the lat/lon are very different from BASINS to CHPD
    which_station_id = '352867'

    for item in coop_stations_to_use:
        if item.station_id == which_station_id:
            get_data(item)
            s_date = item.get_start_date_to_use(basins_stations)
            e_date = item.get_end_date_to_use(basins_stations)
            process_data(item, basins_stations, s_date, e_date)
