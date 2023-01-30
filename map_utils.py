import json
import folium
import branca
import pandas as pd
import numpy as np

import constants
import utils


def draw_polygon_on_map(vis_map, coordinates):

    base_feature_group = folium.FeatureGroup(constants.BOUNDING_POLYGON)
    folium.PolyLine(coordinates, weight=6).add_to(base_feature_group)
    base_feature_group.add_to(vis_map)
    return vis_map


def draw_circles_on_map(vis_map, coordinates, circle_strengths):
    colors = ['#0000FF', '#4169E1', '#8A2BE2', '#4B0082', '#483D8B', '#6A5ACD', '#7B68EE', '#9370DB', '#9400D3',
              '#9932CC', '#BA55D3', '#800080', '#C71585', '#FF00FF', '#FF1493', '#F08080', '#FA8072', '#FF6347',
              '#FF4500', '#FF0000']

    color_map = branca.colormap.LinearColormap(vmin=min(circle_strengths), vmax=max(circle_strengths), colors=colors)

    for i, c in enumerate(coordinates):
        color = color_map.rgb_hex_str(x=circle_strengths[i])
        folium.Circle(location=c, radius=1000,
                      color=color,
                      fill=True, fill_color=color).add_to(vis_map)

    return vis_map


def visualize_pjm_stations():
    map_name = f'PJM Weather Stations'
    tiles = 'OpenStreetMap'

    df = utils.read_ghcnd_data(country='US')
    df = df.loc[df[constants.STATE].isin(constants.PJM_STATES), :]
    df[constants.STATE_ID] = df[constants.STATE].factorize()[0]

    point_coordinates = [tuple(x) for x in df[[constants.LAT, constants.LON]].to_numpy()]
    point_strengths = df[constants.STATE_ID].tolist()

    center_lat = (df[constants.LAT].min() + df[constants.LAT].max()) / 2
    center_lon = (df[constants.LON].min() + df[constants.LON].max()) / 2

    map_width = 1536
    map_height = 864
    vis_map = folium.Map(location=[center_lat, center_lon],
                         width=map_width, height=map_height,
                         tiles=tiles, zoom_start=7)

    vis_map = draw_circles_on_map(vis_map=vis_map, coordinates=point_coordinates, circle_strengths=point_strengths)
    vis_map.save(f'{constants.OUT_FOLDER}{map_name}.html')

    dummy = -32
