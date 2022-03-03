import datetime
import os
import math

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


def read_temperature_file(station_id):
    filename = os.path.join(os.getcwd(), 'resources', 'temperature', station_id + '.txt')
    with open(filename, 'r') as file:
        data = file.readlines()

    split_data = [item.strip('\n').split('\t') for item in data]
    return split_data

def convert_temperature(temperature_f):
    temperature_c = (float(temperature_f) - 32.0) *5/9
    return temperature_c


def calculate_evaporation(temperature_data, latitude):
    latitude_radians = latitude * math.pi/180
    print(latitude_radians)

    counter = 0
    T_a = []
    T_r = []
    evaporations = []

    for item in temperature_data:
        try:
            J = datetime.date(1,int(item[2]),int(item[3])).toordinal() # julian day
            d_r = 1 + 0.033*math.cos(2*math.pi*J/365)
            delta = 0.4093*math.sin(2*math.pi*(284+J)/365)
            w_s = math.acos(-math.tan(latitude_radians)*math.tan(delta))
            R_a = 37.6*d_r*(w_s*math.sin(latitude_radians)*math.sin(delta) +
                            math.cos(latitude_radians)*math.cos(delta)*math.sin(w_s))

            T_min_C = convert_temperature(item[-1])
            T_max_C = convert_temperature(item[-2])
            local_T_a = (T_min_C + T_max_C)/2.0
            local_T_r = T_max_C - T_min_C

            T_a.append(local_T_a)
            T_r.append(local_T_r)

            # let's first just use the local values, we can figure the running average out later
            latent_heat = 2.5 - 0.002361*local_T_a # lambda, but lambda is a keyword

            evap = 0.0023*(R_a/latent_heat)*math.sqrt(local_T_r)*(local_T_a+17.8)
            evaporations.append(evap/25.4)

        except ValueError:
            # leap year...let's just ignore this for now?
            # supposed to use 366 in denominator of d_r if a leap year
            pass


    return evaporations

def plot_evap(evap):
    plt.plot(evap)
    plt.show()

if __name__ == '__main__':
    latitudes = get_latitudes()


    station_id = '72793524234'  # seattle
    seattle_temperature_data = read_temperature_file(station_id)

    latitude_for_verification = -20

    seattle_evaporations = calculate_evaporation(seattle_temperature_data, float(latitudes[station_id]))
    plot_evap(seattle_evaporations)
