import csv
import collections
import datetime
import os
import requests

import common
from dataclasses import asdict
from dateutil.relativedelta import relativedelta

def download_station_inventory_file():
    """
    Downloads the station inventory file for COOP-HPD version 2 from the NOAA

    The station inventory file is updated on an irregular schedule,
    so the function also determines what the URL for the file should be
    Confirms the status_code is 200
    Writes the station inventory file to the src/ directory
    Returns the path to the station inventory file
    """

    station_inv_base_url = 'http://ncei.noaa.gov/data/coop-hourly-precipitation/v2/station-inventory/'
    r = requests.get(station_inv_base_url)
    raw_text = r.content.decode()
    start_index = raw_text.find('HPD_')
    end_index = raw_text.find('.csv')
    filename = raw_text[start_index:end_index + 4]

    r_file = requests.get(station_inv_base_url + filename)
    assert r_file.status_code == 200

    station_inv_file = os.path.join(os.getcwd(), 'src', filename)

    with open(station_inv_file, 'wb') as file:
        file.write(r.content)

    return station_inv_file


def read_coop_file(station_inv_file):
    """
    Reads the C-HPD version 2 station inventory file

    Returns a list of Station objects representing each entry in file
    """

    station_inv_file = os.path.join(os.getcwd(), 'src', 'HPD_v02r02_stationinv_c20200826.csv')
    stations = []

    with open(station_inv_file, 'r') as csv_file:
        station_inv_reader = csv.reader(csv_file)
        header = next(station_inv_reader)
        for row in station_inv_reader:
            por = row[9].split('-')
            stations.append(common.Station(row[0][-6:], row[5], 
                                           common.make_date(por[0]), 
                                           common.make_date(por[1]), 
                                           row[1], row[2], False))

    return stations

def check_codes(basins, coops):
    coop_not_in_basins = 0
    basins_ids = [item.station_id for item in basins]

    exact_match = []
    close_enough = []
    oh_no = []
    not_in_basins = []

    differences = []
    for item in coops:
        if item.station_id in basins_ids:
            for x in basins:
                if item.station_id == x.station_id:
                    assert item.station_id == x.station_id
                    try:
                        assert item.station_name == x.station_name
                        exact_match.append(item)
                    except:
                        try:
                            assert item.station_name[0:4] == x.station_name[0:4]
                            close_enough.append(item)
                        except:
                            oh_no.append(item)
                            print(item.station_id)
                            print(item.station_name + ',' + item.latitude + ',' + item.longitude)
                            print(x.station_name + ',' + x.latitude + ',' + x.longitude)
                            # print(item.station_name, ',', x.station_name)
                            # print(item.latitude, ',', x.latitude)
                            # print(item.longitude, ',', x.longitude)
        else:
            not_in_basins.append(item)
            # print(item.station_name)
            differences.append(item.end_date - item.start_date)

    assert (len(exact_match) + len(close_enough) + len(oh_no) + len(not_in_basins)) == len(coop_stations)

def assign_in_basins_attribute(basins, coops):
    """
    Assigns in_basins attribute

    Iterates through all C-HPD Stations and determine if the station_id
    maches a station_id in the BASINS dataset

    Writes file break_with_basins to determine which stations have
    a break between the end of the BASINS reporting period and the 
    beginning of the C-HPD v2 reporting period

    Returns list of C-HPD stations with in_basins attribute assigned
    """

    basins_ids = [item.station_id for item in basins]
    counter = 0

    with open(os.path.join(os.getcwd(), 'src', 'break_with_basins.csv'), 'w') as file:
        file.write('station_id, station_name, BASINS_start_date, BASINS_end_date, COOP_start_date, COOP_end_date \n')
        for item in coops:
            if item.station_id in basins_ids:
                item.in_basins = True
                for x in basins:
                    if item.station_id == x.station_id:
                        if item.start_date > x.end_date:
                            file.write(item.station_id + ',')
                            file.write(item.station_name + ',')
                            file.write(str(x.start_date.month) + '/' + str(x.start_date.day) + '/' + str(x.start_date.year) + ',')
                            file.write(str(x.end_date.month) + '/' + str(x.end_date.day) + '/' + str(x.end_date.year) + ',')
                            file.write(str(item.start_date.month) + '/' + str(item.start_date.day) + '/' + str(item.start_date.year) + ',')
                            file.write(str(item.end_date.month) + '/' + str(item.end_date.day) + '/' + str(item.end_date.year))
                            file.write('\n')
                            counter += 1

    print(f'There are {counter} stations with a gap between the end of BASINS and the start of the COOP record')
    return coops


def check_years(coops):
    """
    Determines which C-HPD v2 stations to use

    Rules:
    1. If a station is in BASINS and is current, use the station
    2. If a station is in BASINS and is not current, but there is no gap between 
       the BASINS end date and the C-HPD v2 start date,  use the station
    3. If a stations is in BASINS and there is a gap between the BASINS 
       end date and the C-HPD v2 start date, only use the station if there
       are at least 10 years of data from C-HPD v2
    4. If a station is not in BASINS, use the station if it has at least
       10 consecutive years of data
    
    """
    coops_to_use = []

    for item in coops:
        if item.in_basins:
            # TODO finalize this
            # if item.start_date
            if item.end_date <= common.CUTOFF_START_DATE:
                pass
            else:
                coops_to_use.append(item)
        else:
            # if not in BASINS, use if at least ten years of data from some sort of recent past
            if item.station_id == '214546':
                print('debug')
            if relativedelta(item.end_date, item.start_date).years >= 10:
                coops_to_use.append(item)
            else:
                pass
                
    return coops_to_use
            
    


def write_one(dummy_station):

    with open(os.path.join(os.getcwd(), 'src', 'coop_stations_to_use.csv'), 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(asdict(dummy_station[0]).keys())
        for item in dummy_station:
            writer.writerow(asdict(item).values())


def get_earliest_end_date(coops):
    """
    Prints earliest end date in C-HPD v2
    Currently informational only
    """

    end_dates = [item.end_date for item in coops]
    print(f'The earliest end date for a station in C-HPD v2 is {min(end_dates)}')

def get_latest_start_date(coops):
    """
    Prints latest start date in C-HPD v2
    Currently informational only
    """
    start_dates = [item.start_date for item in coops]
    print(f'The latest start date for a station in C-HPD v2 is {max(start_dates)}')

if __name__ == '__main__':
    # if you have the most recent file, you can prevent re-downloading that file
    # by commenting out the download_station_inventory_file() line and 
    # specifying the filepath directly below

    station_inventory_file = os.path.join(os.getcwd(), 'src', 'HPD_v02r02_stationinv_c20200909.csv')
    # station_inventory_file = download_station_inventory_file()

    basins_stations = common.read_basins_file()
    coop_stations = read_coop_file(station_inventory_file)

    coop_stations = assign_in_basins_attribute(basins_stations, coop_stations)
    coops_to_use = check_years(coop_stations)

    # Exploratory functions
    get_earliest_end_date(coop_stations)
    get_latest_start_date(coop_stations)

    write_one(coops_to_use)

    # below function used for exploration; station/code matches deemed acceptable
    # check_codes(basins_stations, coop_stations)
