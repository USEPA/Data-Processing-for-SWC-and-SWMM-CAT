import json

import requests

from passwords import BLS_API_KEY


BLS_READY_MIX_CONC_ID = 'PCU327320327320'
BLS_TRACTOR_SHOVEL_LOADERS_ID = 'PCU33312033312014'

PREFIX = 'CU'
SEASONAL_ADJUSTMENT_CODE = 'U'
PERIODICITY_CODE = 'S'

ENERGY_ITEM_CODE = 'SA0E'
FUEL_UTILITIES_ITEM_CODE = 'SAH2'


def make_id(bls_city_id, item_code):
    """
    Creates a BLS series ID

    Takes a four-digit city ID and a four-digit item code
    Returns a BLS series ID
    """
    return PREFIX + SEASONAL_ADJUSTMENT_CODE + \
        PERIODICITY_CODE + bls_city_id + item_code


def make_ids():
    """
    Creates all series IDs to be obtained from the BLS API

    The cost module of the SWC uses two national-level indices
    (for ready-mix concrete and tractor shovel loaders)
    and two city-specific indices (for energy and fuel utilities)

    Returns a list of series IDs
    """
    items = [BLS_READY_MIX_CONC_ID, BLS_TRACTOR_SHOVEL_LOADERS_ID]

    city_codes = ['0000',  # National
                  'S49G',  # Anchorage AK
                  'S35C',  # Atlanta GA
                  'S11A',  # Boston MA
                  'S23A',  # Chicago IL
                  'S37A',  # Dallas TX
                  'S48B',  # Denver CO
                  'S23B',  # Detroit MI
                  'S49F',  # Honolulu HI
                  'S37B',  # Houston TX
                  'S49A',  # Los Angeles CA
                  'S35B',  # Miami FL
                  'S24A',  # Minneapolis MN
                  'S12A',  # New York NY
                  'S12B',  # Philadelphia PA
                  'S49E',  # San Degio CA
                  'S49B',  # San Francisco CA
                  'S49D'  # Seattle WA
                  ]
    for code in city_codes:
        items.append(make_id(code, ENERGY_ITEM_CODE))
        items.append(make_id(code, FUEL_UTILITIES_ITEM_CODE))

    return items


def get_data(series_ids_list, registration_key, year):
    """
    Gets data from BLS API

    Returns JSON response from API
    """

    base_url = 'https://api.bls.gov/publicAPI/v2/timeseries/data/'
    headers = {'Content-type': 'application/json'}

    data = json.dumps(
        {"seriesid": series_ids_list,
         "startyear": year, "endyear": year,
         "catalog": "false",
         "calculations": "false",
         "annualaverage": "true",
         "registrationKey": registration_key})

    r = requests.post(base_url, data=data, headers=headers)

    return r.json()


def make_request_model(four_ids, year, registration_key):
    """
    Makes request model to put in cache file

    Each request model has four IDs (two city-specific
    and two national) and the year for the data

    Returns request model
    """

    request_model = {
        "requestModel": {
                        "seriesid": four_ids,
                        "startyear": str(year),
                        "endyear": str(year),
                        "catalog": False,
                        "calculations": False,
                        "annualaverage": True,
                        "registrationKey": registration_key
                        }
                    }

    return json.dumps(request_model, separators=(',', ':'))


def make_response_model(four_series):
    """
    Makes response model to put in cache file

    Each response model has four series of data

    Returns response model
    """

    response_model = {
        "responseModel": {
            "status": "REQUEST_SUCCEEDED",
            "responseTime": "524",
            "message": [],
            "Results": {
                "series": four_series
                }
            }
        }

    return json.dumps(response_model, separators=(',', ':'))


def get_match(data, i, ids):
    """
    Returns series results corresponding to integer i
    """
    return [item for item in data if item['seriesID'] == ids[i]][0]


def write_cache_file(data1, data2, ids, registration_key, year):
    """
    Writes cache file

    Returns national series, used to calculate national Index
    """

    all_series = data1['Results']['series'] + data2['Results']['series']

    # Handle all_series[0:1] separately
    # These are the series used for all cities
    ready_mix_conc_series = get_match(all_series, 0, ids)
    tractor_shovel_loaders_series = get_match(all_series, 1, ids)

    to_file = ''

    # Start at 2 because that's where city-specific series start
    for i in range(2, len(all_series) - 1, 2):
        local_list = [ids[i], ids[i+1], ids[0], ids[1]]

        request_model = make_request_model(local_list, year, registration_key)

        response_model = make_response_model(
            [get_match(all_series, i, ids),
             get_match(all_series, i+1, ids),
             ready_mix_conc_series,
             tractor_shovel_loaders_series])

        to_file += request_model[0:-1] + ','
        to_file += response_model[1:]
        to_file += '\n'

        if local_list[0][4:8] == '0000':
            for_national_index = response_model

    with open('costRegionalizationCache.txt', 'w') as cache_file:
        cache_file.write(to_file)

    return for_national_index


def calculate_national_index(national_series, year):
    """
    Calculates national index for a given year

    The national index value DEFAULT_YYYY_NATIONAL_INDEX is used in
    SWC in CostRegionalizationServiceImpl.java

    """

    C0_INTERCEPT = -19.4
    C1_READY_MIX = 0.113
    C2_TRACTOR_SHOVEL = 0.325
    C3_ENERGY = 0.096
    C4_FUEL_UTILS = 0.398

    series = json.loads(national_series)['responseModel']['Results']['series']
    ids = [x['seriesID'] for x in series]

    assert ids[0][-4:] == ENERGY_ITEM_CODE
    assert ids[1][-4:] == FUEL_UTILITIES_ITEM_CODE
    assert ids[0][4:8] and ids[1][4:8] == '0000'
    assert ids[2] == BLS_READY_MIX_CONC_ID
    assert ids[3] == BLS_TRACTOR_SHOVEL_LOADERS_ID
    assert {x['data'][0]['periodName'] for x in series} == {'Annual'}

    values = [float(x['data'][0]['value']) for x in series]

    national_index = (C0_INTERCEPT +
                      C1_READY_MIX * values[2] +
                      C2_TRACTOR_SHOVEL * values[3] +
                      C3_ENERGY * values[0] +
                      C4_FUEL_UTILS * values[1])

    print(f'National index for year {year} is: {round(national_index, 2)}')


if __name__ == '__main__':
    YEAR_TO_GET = 2020
    series_ids = make_ids()

    # the system-allowed limit is 25 series, so go in two steps
    first_data = get_data(series_ids[0:24], BLS_API_KEY, YEAR_TO_GET)
    second_data = get_data(series_ids[24:], BLS_API_KEY, YEAR_TO_GET)

    # for debugging
    # with open('first_data.json', 'w') as file:
    #     file.write(json.dumps(first_data))
    # with open('second_data.json', 'w') as file:
    #     file.write(json.dumps(second_data))

    with open('first_data.json', 'r') as file:
        first_data = json.load(file)

    with open('second_data.json', 'r') as file:
        second_data = json.load(file)

    national_response = write_cache_file(
        first_data, second_data, series_ids, BLS_API_KEY, YEAR_TO_GET)
    calculate_national_index(national_response, YEAR_TO_GET)
