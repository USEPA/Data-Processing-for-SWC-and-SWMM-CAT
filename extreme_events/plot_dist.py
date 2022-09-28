import os
import itertools

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

def read_nrcs_data(dist_file):
    with open(dist_file, 'r') as file:
        data = file.readlines()

    header = data.pop(0)

    new_data = [item.split() for item in data if item != '\n']

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

    return percent_of_duration_values, stuff

def plot_precip(precips, names):
    times = [x/10 for x in range(0, 241)]
    palette = itertools.cycle(sns.color_palette("Paired"))

    graph_spots = list(range(1, 7))

    fig = plt.figure()
    for (name, graph_spot) in zip(names, graph_spots):

        ax = fig.add_subplot(2, 3, graph_spot)

        for x in name:
            if x == 'SCS_I':
                color = 'dimgray'
            elif x == 'SCS_II':
                color = [0.9375, 0.9375, 0.859375]
            else:
                color = next(palette)
            ax.plot(times, precips[x], '-', label=x, color=color)

        ax.set_xlim(0, 24)
        ax.set_ylim(0, 1)

        x_major_ticks = np.arange(0, 25, 4)
        x_minor_ticks = np.arange(0, 25, 2)

        y_major_ticks = np.arange(0, 1.1, 0.5)
        y_minor_ticks = np.arange(0, 1.1, 0.1)

        ax.set_xticks(x_major_ticks)
        ax.set_xticks(x_minor_ticks, minor=True)
        ax.set_yticks(y_major_ticks)
        ax.set_yticks(y_minor_ticks, minor=True)
        ax.tick_params(axis='both', which='major', labelsize='large')

        ax.grid(which='minor', alpha=0.2)
        ax.grid(which='major', alpha=0.5)

        ax.legend(fontsize='large')
        ax.set_xlabel('Time (hours)', fontsize='large')
        ax.set_ylabel('Fraction of 24-hour rainfall', fontsize='large')

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


def plot_noaa_data():
    noaa_filename = os.path.join('for_plotting', 'sa_convective_24h_temporal.csv')

    test_1, test_2 = read_noaa_data(noaa_filename)
    plot_noaa_precip(test_1, test_2[0:9])
    plot_noaa_precip(test_1, test_2[9:18])
    plot_noaa_precip(test_1, test_2[18:27])
    plot_noaa_precip(test_1, test_2[27:36])
    plot_noaa_precip(test_1, test_2[36:45])


if __name__ == '__main__':
    distributions = []
    distributions.append(['MSE_1', 'MSE_2', 'MSE_3', 'MSE_4', 'MSE_5', 'MSE_6'])
    distributions.append(['NOAA_A', 'NOAA_B', 'NOAA_C', 'NOAA_D'])
    distributions.append(['NRCC_A', 'NRCC_B', 'NRCC_C', 'NRCC_D'])
    distributions.append(['NV_N', 'NV_S', 'NV_W'])
    distributions.append(['CA_1', 'CA_2', 'CA_3', 'CA_4', 'CA_5', 'CA_6'])
    distributions.append(['SCS_I', 'SCS_IA', 'SCS_II', 'SCS_III'])

    distribution_data = {}
    for distribution_list in distributions:
        for x in distribution_list:
            distribution_data[x] = read_nrcs_data(os.path.join(
                'nrcs_tables', x + '.txt'))

    plot_precip(distribution_data, distributions)


