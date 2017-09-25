#!/bin/python

""" Routine to download & analyze data characterizing optimized bioenergy landscapes and plot associated soil
distributions.
"""

import csv
from db_tools import list_to_sql
import matplotlib.pyplot as plt
import numpy as np
from operator import itemgetter
import soil_plotter
import sqlite3


def soils_analysis(landscape_fpath, sand_column, silt_column, clay_column, size_column, color_column, figure_name,
                   title='', legend_title=''):

    # open .csv-format landscape data file and verify data columns
    input_object = open(landscape_fpath, 'rU')
    lines = csv.reader(input_object)
    column_names = lines.next()

    sand_index = column_names.index(sand_column)
    silt_index = column_names.index(silt_column)
    clay_index = column_names.index(clay_column)
    size_index = column_names.index(size_column)
    color_index = column_names.index(color_column)

    print
    print "Please verify:"
    print "   Soil sand content data being extracted from column %i, '%s'" % (sand_index, sand_column)
    print "   Soil silt content data being extracted from column %i, '%s'" % (silt_index, silt_column)
    print "   Soil clay content data being extracted from column %i, '%s'" % (clay_index, clay_column)
    print "   Point size data data being extracted from column %i, '%s'" % (size_index, size_column)
    print "   Point color data being extracted from column %i, '%s'" % (color_index, color_column)
    print

    raw_input("Press ENTER to continue:")
    print

    # read each line of soil data into an intermediary data structure, using surface texture as an identifier
    print "Reading soil data data into database to facilitate analysis & sorting..."
    soil_data = [['id', 'area', 'color_values'], ['TEXT', 'REAL', 'REAL']]

    for e, line in enumerate(lines):

        # determine soil texture
        sand_string = line[sand_index]
        if sand_string != '#N/A':
            sand = float(line[sand_index])/100.0
            silt = float(line[silt_index])/100.0
            clay = float(line[clay_index])/100.0
            size = float(line[size_index])/100.0
            color = float(line[color_index])

            # convert soil texture to string, and save to intermediate data list
            id = '%.2f_%.2f_%.2f' % (sand, silt, clay)
            soil_data.append([id, size, color])

    # upload soil data to database
    db_fpath = 'soils.db'
    list_to_sql(soil_data, db_fpath, 'soils')

    # extract list of unique soils, and associated total size and average color data values
    print "Determining total point size and associated area-weighted color for each unique soil in the dataset..."
    con = sqlite3.connect(db_fpath)
    with con:
        cur = con.cursor()
        cur.execute("SELECT id, SUM(area), AVG(color_values) FROM soils GROUP BY id")
        processed_data = cur.fetchall()

    # sort by size (so smallest points can be printed on top of larger ones) and extract soil texture data
    processed_data.sort(key=itemgetter(1), reverse=True)

    soil_strings, sizes, color_scalars = zip(*processed_data)
    textures = []
    for soil_string in soil_strings:
        texture = soil_string.split('_')
        for i in range(len(texture)):
            texture[i] = float(texture[i])
        textures.append(tuple(texture))

    # normalize & scale areas
    scalar = 12000
    areas = np.asarray(sizes)
    total_area = np.sum(areas)
    areas /= total_area
    areas *= scalar

    # create soil texture triangle plot
    soil_plotter.plot_triangle_axes()
    soil_plotter.plot_triangle_grid()
    soil_plotter.plot_simple_classes()
    # soil_plotter.plot_usda_classes()
    soil_plotter.soil_plotter(textures, areas, color_scalars, custom_scalar_range=(0, 60))

    # create legend
    custom_scale = [0.0, 15.0, 30.0, 45.0, 60.0]
    scale_colors = [soil_plotter.color_scale(soil_plotter.c2, soil_plotter.c2_light, X, (min(custom_scale), max(custom_scale))) for X in custom_scale]
    for i, entry in enumerate(custom_scale):
        plt.plot([0, 0], [0, 0], color=scale_colors[i], label=str(custom_scale[i]), linewidth=12)
    l = plt.legend(bbox_to_anchor=(1.13, 1.1), title=legend_title, prop={'size': 14})
    plt.setp(l.get_title(), multialignment='center')

    # add title and save
    plt.text(-0.5, 1.2, title, ha='center', va='center', fontsize=15)
    plt.savefig(figure_name)
    plt.close()
    print


soils_analysis('landscape_iii.csv', 'sand', 'silt', 'clay', 'area_ha_', 'n_opt', 'landscape_iii.png',
               title="205 USD (Mg $\mathregular{CO_{2}}$eq$\mathregular{)^{-1}}$",
               legend_title="Optimal fertilizer\napplication rate\n(kg N $\mathregular{ha^{-1}}$)")