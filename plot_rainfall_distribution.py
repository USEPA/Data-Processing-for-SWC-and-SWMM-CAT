import os

import contextily as ctx
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import cartopy.io.shapereader as shpreader

import seaborn as sns
import itertools
import geopandas as gpd



def read_shapefile():
    fname = os.path.join(
        'rainfall_distribution', 'RainfallDistribution.shp')

    rainfall_distribution = gpd.read_file(fname)
    rainfall_distribution = rainfall_distribution.to_crs(epsg=4326)

    return rainfall_distribution


def plot_states(distribution):

    fig = plt.figure(figsize=(8,6))
    ax = fig.add_axes([0, 0, 1, 1], projection=ccrs.LambertConformal())

    ax.set_extent([-125, -66.5, 20, 50], ccrs.Geodetic())
    shapename = 'admin_1_states_provinces_lakes'
    states_shp = shpreader.natural_earth(resolution='110m',
                                         category='cultural', name=shapename)


    for state in shpreader.Reader(states_shp).geometries():
        # pick a default color for the land with a black outline
        facecolor = [0.9375, 0.9375, 0.859375]
        edgecolor = 'black'

        ax.add_geometries([state], ccrs.PlateCarree(),
                          facecolor=facecolor, edgecolor=edgecolor)

    palette = itertools.cycle(sns.color_palette("Paired"))

    distributions = []
    distributions.append(['MSE_1', 'MSE_2', 'MSE_3', 'MSE_4', 'MSE_5', 'MSE_6'])
    distributions.append(['NOAA_A', 'NOAA_B', 'NOAA_C', 'NOAA_D'])
    distributions.append(['NRCC_A', 'NRCC_B', 'NRCC_C', 'NRCC_D'])
    distributions.append(['NV_N', 'NV_S', 'NV_W'])
    distributions.append(['CA_1', 'CA_2', 'CA_3', 'CA_4', 'CA_5', 'CA_6'])
    distributions.append(['SCS_IA', 'SCS_III'])

    LegendElement = []
    counter = 0
    hatch = None
    for x in distributions:
        for y in x:
            if counter >= 24:
                hatch = '\\\\'
            elif counter >= 12:
                hatch = '///'
            color = next(palette)
            ax.add_geometries(distribution.loc[distribution['rf_value'] == y]['geometry'],
                crs = ccrs.PlateCarree(), edgecolor='black', facecolor=color, alpha=0.5, hatch=hatch)

            patch = mpatches.Patch(facecolor=color, label=y, hatch=hatch)
            LegendElement.append(patch)

            counter += 1

    patch = mpatches.Patch(facecolor='dimgray', label='SCS_I')
    LegendElement.insert(-2, patch)
    patch = mpatches.Patch(facecolor=facecolor, label='SCS_II')
    LegendElement.insert(-1, patch)
    ax.legend(handles = LegendElement, loc='upper right')
    plt.show()

if __name__ == '__main__':
    rd = read_shapefile()
    plot_states(rd)