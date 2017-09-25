#!/bin/python

""" Routine to plot a distribution of soil on a soil texture triangle, with custom point sizing and coloring.  Textures
must be defined as tuples of (sand fraction, silt fraction, clay fraction).
"""


import matplotlib.pyplot as plt


# RGV values defining a custom colorblind-safe color palette, modified from
# http://mkweb.bcgsc.ca/colorblind/img/colorblindness.palettes.trivial.png
c1 = (0/255.0, 0/255.0, 0/255.0)        # black
c2 = (0/255.0, 114/255.0, 178/255.0)    # blue
c3 = (86/255.0, 180/255.0, 233/255.0)   # sky blue
c4 = (204/255.0, 121/255.0, 167/255.0)  # reddish purple
c5 = (0/255.0, 158/255.0, 115/255.0)    # bluish green
c6 = (213/255.0, 94/255.0, 0/255.0)     # vermillion
c7 = (230/255.0, 159/255.0, 0/255.0)    # orange
c8 = (240/255.0, 228/255.0, 66/255.0)   # yellow
c2_light = (185/255.0, 216/255.0, 233/255.0)    # custom light blue


def color_scale(high_color_rgb, low_color_rgb, scalar, scalar_range):
    """ Define a color between high_color_rgb and low_color_rgb corresponding to where the scalar value sits withing
    the scalar_range
    """
    span = min((scalar-scalar_range[0]) / (scalar_range[1]-scalar_range[0]), 1.0)
    red = low_color_rgb[0] + span * (high_color_rgb[0]-low_color_rgb[0])
    green = low_color_rgb[1] + span * (high_color_rgb[1]-low_color_rgb[1])
    blue = low_color_rgb[2] + span * (high_color_rgb[2]-low_color_rgb[2])
    color = (red, green, blue)
    return color


def transpose(texture):
    """ Convert soil texture tuples in the form (sand, silt, clay) to cartesian coordinates (x, y)
    """
    sand, silt, clay = texture
    x = (-clay/2.0) - sand
    y = clay
    return x, y


def plot_triangle_axes(font_size=14, color='k', zorder=1):
    """ Plot triangular axes, then add axis labels
    """
    # plot outer axis boundaries
    corners = [(0, 0), (-1, 0), (-.5, 1), (0, 0)]
    xy = zip(*corners)
    plt.plot(xy[0], xy[1], color=color, marker=None, linewidth=1.5, zorder=zorder)
    plt.axis('off')

    # add triangular axis labels
    plt.text(-0.48, -0.15, 'sand %', ha='center', va='center', fontsize=font_size, color=color)
    plt.text(-0.9, 0.55, 'clay %', ha='center', va='center', fontsize=font_size, color=color, rotation=60)
    plt.text(-0.1, 0.55, 'silt %', ha='center', va='center', fontsize=font_size, color=color, rotation=-60)


def plot_triangle_grid(font_size=12, color='silver', font_color='k', zorder=0):
    """ Plot triangular axes, then add axis labels and background grid
    """
    sand_grid = [
        [(.9, 0, .1), (.9, .1, -0.05), '90'],
        [(.8, 0, .2), (.8, .2, -0.05), '80'],
        [(.7, 0, .3), (.7, .3, -0.05), '70'],
        [(.6, 0, .4), (.6, .4, -0.05), '60'],
        [(.5, 0, .5), (.5, .5, -0.05), '50'],
        [(.4, 0, .6), (.4, .6, -0.05), '40'],
        [(.3, 0, .7), (.3, .7, -0.05), '30'],
        [(.2, 0, .8), (.2, .8, -0.05), '20'],
        [(.1, 0, .9), (.1, .9, -0.05), '10'],
    ]
    for gridline_parameters in sand_grid:
        x0, y0 = transpose(gridline_parameters[0])
        x1, y1 = transpose(gridline_parameters[1])
        plt.plot((x0, x1), (y0, y1), color=color, marker=None, linewidth=0.5, zorder=zorder)
        plt.text(x1, y1, gridline_parameters[2], ha='left', va='top', color=font_color, fontsize=font_size)

    silt_grid = [
        [(.1, .9, 0), (-0.05, .9, .15), '90'],
        [(.2, .8, 0), (-0.05, .8, .25), '80'],
        [(.3, .7, 0), (-0.05, .7, .35), '70'],
        [(.4, .6, 0), (-0.05, .6, .45), '60'],
        [(.5, .5, 0), (-0.05, .5, .55), '50'],
        [(.6, .4, 0), (-0.05, .4, .65), '40'],
        [(.7, .3, 0), (-0.05, .3, .75), '30'],
        [(.8, .2, 0), (-0.05, .2, .85), '20'],
        [(.9, .1, 0), (-0.05, .1, .95), '10'],
    ]
    for gridline_parameters in silt_grid:
        x0, y0 = transpose(gridline_parameters[0])
        x1, y1 = transpose(gridline_parameters[1])
        plt.plot((x0, x1), (y0, y1), color=color, marker=None, linewidth=0.5, zorder=zorder)
        plt.text(x1, y1, gridline_parameters[2], ha='left', va='bottom', color=font_color, fontsize=font_size)

    clay_grid = [
        [(0, .1, .9), (.15, 0, .9), '90'],
        [(0, .2, .8), (.25, 0, .8), '80'],
        [(0, .3, .7), (.35, 0, .7), '70'],
        [(0, .3, .6), (.45, 0, .6), '60'],
        [(0, .5, .5), (.55, 0, .5), '50'],
        [(0, .6, .4), (.65, 0, .4), '40'],
        [(0, .7, .3), (.75, 0, .3), '30'],
        [(0, .8, .2), (.85, 0, .2), '20'],
        [(0, .9, .1), (.95, 0, .1), '10'],
    ]
    for gridline_parameters in clay_grid:
        x0, y0 = transpose(gridline_parameters[0])
        x1, y1 = transpose(gridline_parameters[1])
        plt.plot((x0, x1), (y0, y1), color=color, marker=None, linewidth=0.5, zorder=zorder)
        plt.text(x1, y1, gridline_parameters[2], ha='right', va='bottom', color=font_color, fontsize=font_size)


def plot_simple_classes(font_size=10, color='k', zorder=2):
    """ Plot boundaries and labels for simplified soil texture groupings, defined wuch that soils with > 65% sand
    content are designated 'sandy', those with > 35% clay content are 'clayey', those with > 65% silt content are
    'silty', and all others are 'loamy'
    """
    boundaries = [(-0.65, 0), (-0.825, 0.35), (-0.175, 0.35), (-0.35, 0)]
    xy = zip(*boundaries)
    plt.plot(xy[0], xy[1], color='k', marker=None, linewidth=1, zorder=-1)
    plt.text(-0.5, 0.175, 'loamy', color=color, ha='center', va='center', fontsize=font_size, zorder=zorder)
    plt.text(-0.825, 0.125, 'sandy', color=color, ha='center', va='center', fontsize=font_size, zorder=zorder)
    plt.text(-0.5, 0.55, 'clayey', color=color, ha='center', va='center', fontsize=font_size, zorder=zorder)
    plt.text(-0.175, 0.125, 'silty', color=color, ha='center', va='center', fontsize=font_size, zorder=zorder)


def plot_usda_classes(font_size=10, color='k', zorder=2):
    """ Plot boundaries and labels for the standard USDA soil texture grouping system with its 12 different soil
    texture classes (e.g., 'sandy loam', 'sandy clay loam', 'sandy clay', etc.)
    """
    soil_class_boundaries = {
        "sand": [(.85, .15, 0), (0.9, 0, 0.1)],
        "loamy sand": [(.7, 0.3, 0), (.85, 0, .15)],
        "silt": [(.2, .8, 0), (.08, .8, .12), (0, .88, .12)],
        "middle": [(.45, 0, .55), (.45, .28, .27), (0, .73, .27)],
        "silt loam": [(.5, .5, 0), (.23, .5, .27)],
        "clay": [(.45, .15, .4), (0, .6, .4)],
        "silts": [(0, .4, .6), (.2, .4, .4), (.2, .53, .27)],
        "sandy clay": [(.65, 0, .35), (.45, .2, .35)],
        "sandy loam": [(.8, 0, .2), (.52, .28, .2), (.45, .28, .27)],
        "loam": [(.52, .28, .2), (.52, .41, .07), (.43, .5, .07)]
    }

    for key in soil_class_boundaries:
        vertex_list = soil_class_boundaries[key]
        vertices_x = []
        vertices_y = []
        for vertex in vertex_list:
            x, y = transpose(vertex)
            vertices_x.append(x)
            vertices_y.append(y)
        plt.plot(vertices_x, vertices_y, color=color, marker=None, linewidth=0.5, zorder=zorder)

    soil_class_lables = {
        "sand": (.92, .05, .03),
        "loamy\nsand": (.81, .15, .04),
        "sandy\nloam": (.62, .26, .12),
        "sandy\nclay loam": (.6, .12, .28),
        "sandy\nclay": (.52, .07, .41),
        "loam": (.41, .42, .17),
        "clay\nloam": (.33, .33, .34),
        "clay": (.23, .23, .54),
        "silt": (.08, .87, .05),
        "silt\nloam": (.23, .63, .14),
        "silty\nclay": (.06, .47, .47),
        "silty\nclay loam": (.1, .57, .33),
    }

    for key in soil_class_lables:
        center = soil_class_lables[key]
        x, y = transpose(center)
        plt.text(x, y, key, color=color, ha='center', va='center', fontsize=font_size, zorder=zorder)


def soil_plotter(textures, sizes, color_scalars, custom_scalar_range='', zorder=1):
    """ Plot each soil in 'textures' with a filled circular marker of point size defined in 'sizes' and RGB color
    defined in 'color_scalars'
    """
    print 'Creating soil texture triangle point cloud...'
    if custom_scalar_range:
        color_scalar_range = custom_scalar_range
    else:
        color_scalar_range = (min(color_scalars), max(color_scalars))

    for e, texture in enumerate(textures):
        x, y = transpose(texture)
        color = color_scale(c2, c2_light, color_scalars[e], color_scalar_range)
        plt.scatter(x, y, s=sizes[e], color=color, zorder=zorder)
    print


def test(figure_name):
    # define a list of dummy soil data in the format [[(texture tuple), size, color_scalar], ...]
    dummy_data = [
        [(.60, .20, .20), 100, 3.0],
        [(.20, .20, .60), 200, 2.0],
        [(.20, .60, .20), 300, 1.0]
    ]
    dummy_textures, dummy_sizes, dummy_color_scalars = zip(*dummy_data)

    plot_triangle_axes()
    plot_triangle_grid()
    # plot_simple_classes()
    plot_usda_classes()
    soil_plotter(dummy_textures, dummy_sizes, dummy_color_scalars)
    plt.savefig(figure_name)


