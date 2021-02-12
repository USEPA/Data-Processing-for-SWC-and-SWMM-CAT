import os
import numpy as np
import matplotlib.pyplot as plt

def read_nrcs_data(dist_file):
    with open(dist_file, 'r') as file:
        data = file.readlines()

    header = data.pop()

    new_data = [item.split() for item in data if item != '\n']
    header = new_data.pop(0)
    print(header)

    flat_precip = [float(x) for item in new_data for x in item]

    return flat_precip

def read_noaa_data(dist_file):
    with open(dist_file, 'r') as file:
        data = file.readlines()

    # get the chunks of data we need
    all_data = []
    first_quartile = data[13:22]
    second_quartile = data[26:35]
    third_quartile = data[39:48]
    fourth_quartile = data[52:61]
    all_cases = data[65:74]

    all_data.append(first_quartile)
    all_data.append(second_quartile)
    all_data.append(third_quartile)
    all_data.append(fourth_quartile)
    all_data.append(all_cases)

    percent_of_duration = data[12].strip('\n').split(',')[1:]
    percent_of_duration_values = [float(x) for x in percent_of_duration]

    stuff = []
    for x in all_data:
        for i in x:
            values = i.strip('\n').split(',')[1:]
            stuff.append([float(value) for value in values])
            # print(stuff)
            # break

    return percent_of_duration_values, stuff

def plot_precip(precip):
    times = [x/10 for x in range(0, 241)]
    fig = plt.figure()
    plt.plot(times, precip, '-')
    plt.xlim(0, 24)
    plt.ylim(0, 1)

    ax = fig.add_subplot(1, 1, 1)

    x_major_ticks = np.arange(0, 25, 4)
    x_minor_ticks = np.arange(0, 25, 2)

    y_major_ticks = np.arange(0, 1.1, 0.2)
    y_minor_ticks = np.arange(0, 1.1, 0.1)

    ax.set_xticks(x_major_ticks)
    ax.set_xticks(x_minor_ticks, minor=True)
    ax.set_yticks(y_major_ticks)
    ax.set_yticks(y_minor_ticks, minor=True)

    ax.grid(which='minor', alpha=0.2)
    ax.grid(which='major', alpha=0.5)

    plt.show()

def plot_noaa_precip(x, y):

    fig = plt.figure()
    for item in y:
        plt.plot(x, item)

    plt.xlim(0, 100)
    plt.ylim(0, 100)

    ax = fig.add_subplot(1, 1, 1)

    x_major_ticks = np.arange(0, 101, 25)
    x_minor_ticks = np.arange(0, 101, 5)

    y_major_ticks = np.arange(0, 101, 10)
    # y_minor_ticks = np.arange(0, 1.1, 0.1)

    ax.set_xticks(x_major_ticks)
    ax.set_xticks(x_minor_ticks, minor=True)
    ax.set_yticks(y_major_ticks)
    # ax.set_yticks(y_minor_ticks, minor=True)

    ax.grid(which='minor', alpha=0.2)
    ax.grid(which='major', alpha=0.5)

    plt.show()


if __name__ == '__main__':
    nrcs_filename = os.path.join('for_plotting', 'Type_NV_S.tbl')
    processed_nrcs_precip = read_nrcs_data(nrcs_filename)
    noaa_filename = os.path.join('for_plotting', 'sa_convective_24h_temporal.csv')
    plot_precip(processed_nrcs_precip)
    test_1, test_2 = read_noaa_data(noaa_filename)
    plot_noaa_precip(test_1, test_2[0:9])
    plot_noaa_precip(test_1, test_2[9:18])
    plot_noaa_precip(test_1, test_2[18:27])
    plot_noaa_precip(test_1, test_2[27:36])
    plot_noaa_precip(test_1, test_2[36:45])

