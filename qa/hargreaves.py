import calendar
import datetime
import os
import math
import statistics

import matplotlib.pyplot as plt


def get_latitudes():
    filename = os.path.join(os.getcwd(), 'resources', 'D4EM_PMET_updated.txt')
    with open(filename, 'r') as file:
        data = file.readlines()

    split_data = [item.strip('\n').split('\t') for item in data]
    header = split_data.pop(0)

    lat_dict = {}
    for x in split_data:
        lat_dict[x[0]] = x[4]

    return lat_dict


def read_adjustments(scenario):
    filename = os.path.join(os.getcwd(), 'resources', scenario + '.txt')
    with open(filename, 'r') as file:
        data = file.readlines()

    split_data = [item.strip('\n').split('\t') for item in data]
    header = split_data.pop(0)

    adjustment_dict = {}
    for x in split_data:
        monthly_adjustments = x[1:-1]
        adjustment_dict[x[0]] = {k: float(v) for k, v in zip(range(1, 13), monthly_adjustments)}

    return adjustment_dict


def read_temperature_file(station_id):
    filename = os.path.join(os.getcwd(), 'resources', 'temperature', station_id + '.txt')
    with open(filename, 'r') as file:
        data = file.readlines()

    split_data = [item.strip('\n').split('\t') for item in data]
    return split_data


def convert_temperature(temperature_f):
    temperature_c = (temperature_f - 32.0) *5/9
    return temperature_c


def adjust_temperatures(base_temperature_data, adjustments):
    pass


def calculate_evaporation(temperature_data, latitude, adjustments):
    latitude_radians = latitude * math.pi/180

    counter = 0
    T_a = []
    T_r = []
    evaporations = []
    months = []

    for item in temperature_data:
        month = int(item[2])
        J_with_year = datetime.date(int(item[1]),month,int(item[3])).toordinal()
        J = J_with_year - datetime.datetime(int(item[1]), 1, 1).toordinal() + 1 # julian day

        if calendar.isleap(int(item[1])):
            days_per_year = 366
        else:
            days_per_year = 365

        d_r = 1 + 0.033*math.cos(2*math.pi*J/days_per_year)
        delta = 0.4093*math.sin(2*math.pi*(284+J)/days_per_year)
        w_s = math.acos(-math.tan(latitude_radians)*math.tan(delta))
        R_a = 37.6*d_r*(w_s*math.sin(latitude_radians)*math.sin(delta) +
                        math.cos(latitude_radians)*math.cos(delta)*math.sin(w_s))

        T_min_C = convert_temperature(float(item[-1]) + adjustments[month])
        T_max_C = convert_temperature(float(item[-2]) + adjustments[month])
        local_T_a = (T_min_C + T_max_C)/2.0
        local_T_r = T_max_C - T_min_C

        T_a.append(local_T_a)
        T_r.append(local_T_r)

        # running average
        if counter < 7:
            running_average_T_a = statistics.mean(T_a)
            running_average_T_r = statistics.mean(T_r)
        else:
            running_average_T_a = statistics.mean(T_a[-7:])
            running_average_T_r = statistics.mean(T_r[-7:])

        latent_heat = 2.5 - 0.002361*running_average_T_a # lambda, but lambda is a keyword

        evap = 0.0023*(R_a/latent_heat)*math.sqrt(running_average_T_r)*(running_average_T_a+17.8)
        evaporations.append(evap/25.4)
        months.append(month)

        counter += 1

    return (evaporations, months)

def aggregate_evaporations(evaporations, months):
    evap_dict = {k: [] for k in range(1, 13)}

    for evap, month in zip(evaporations, months):
        evap_dict[month].append(evap)

    monthly_dict = {k: 0 for k in range(1, 13)}
    for key, value in evap_dict.items():
        monthly_dict[key] = statistics.mean(value)

    return monthly_dict


def plot_evap(evaps):
    for evap in evaps:
        plt.plot(evap)
    plt.show()

if __name__ == '__main__':
    latitudes = get_latitudes()
    scenarios = ['TEMP2035HotDry', 'TEMP2035Central', 'TEMP2035WetWarm',
                 'TEMP2060HotDry', 'TEMP2060Central', 'TEMP2060WetWarm']
    adjustment_data = {}
    for scenario in scenarios:
        adjustment_data[scenario] = read_adjustments(scenario)

    station_ids = [
        '70273526409', # anchorage
        'USC00519534', # honolulu
        '72793524234', # seattle
        '72466693067', # denver
        '72658014922', # minneapolis
        '72530094846', # chicago
        '72202012839', # miami
        '72503394728', # new york
        '72278403184', # phoenix
        '72219503888', # atlanta
        ]

    no_adjustments = {k: 0 for k in range(1, 13)}
    all_evaporations = {} # do we need to save all these values?
    monthly_evaporation = {}
    diffs = {}

    for station_id in station_ids:
        monthly_evaporation[station_id] = {}
        all_evaporations[station_id] = {}
        diffs[station_id] = {}

        temperature_data = read_temperature_file(station_id)

        all_evaporations[station_id]['base'], months = calculate_evaporation(
            temperature_data, float(latitudes[station_id]), no_adjustments)

        monthly_evaporation[station_id]['base'] = aggregate_evaporations(all_evaporations[station_id]['base'], months)

        for scenario in scenarios:
            all_evaporations[station_id][scenario], a_months = calculate_evaporation(
                temperature_data, float(latitudes[station_id]), adjustment_data[scenario][station_id])

            monthly_evaporation[station_id][scenario] = aggregate_evaporations(all_evaporations[station_id][scenario], months)

            diffs[station_id][scenario] = {}

            for k in monthly_evaporation[station_id]['base'].keys():
                diffs[station_id][scenario][k] = monthly_evaporation[station_id][scenario][k] - monthly_evaporation[station_id]['base'][k]




        # for debugging
    to_file = ''
    for station_id in station_ids:
        for scenario in scenarios:
            line = f'{station_id},{scenario},'
            for i in range (1, 13):
                line += f'{diffs[station_id][scenario][i]:.3f},'
                # print(diffs[station_id][scenario][i])
            to_file += f'{line}\n'

    with open(os.path.join('qa', 'evap_change.csv'), 'w') as file:
        file.write(to_file)


    monthly_evap_to_file = ''
    scenario = 'base'
    for station_id in station_ids:
        line = f'{station_id},base,'
        for i in range (1, 13):
            line += f'{monthly_evaporation[station_id][scenario][i]:.3f},'
        monthly_evap_to_file += f'{line}\n'

    with open(os.path.join('qa', 'monthly_evap.csv'), 'w') as file:
        file.write(monthly_evap_to_file)



        # plot_evap([all_evaporations[station_id]['base'], all_evaporations[station_id][scenarios[0]]])


        # rounded_evap = {}
        # for key in monthly_evaporation['base'].keys():
        #     rounded_evap[key] = round(monthly_evaporation['base'][key], 3)
        # print(rounded_evap)

        # for key in monthly_evaporation['TEMP2035HotDry'].keys():
        #     rounded_evap[key] = round(monthly_evaporation['TEMP2035HotDry'][key], 3)

        # print(rounded_evap)

        # for key in a_monthly_evaporation.keys():
        #     rounded_evap[key] = round(a_monthly_evaporation[key], 3)



