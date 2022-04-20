from pathlib import Path
import sys
import yaml
import time
import os

import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt

DIR = Path('..')
sys.path.insert(0, str(DIR))
from SCanalyzer import SCanalyzer
from SCanalyzer.busSim import BusSim, Config
from SCanalyzer.busSim.manager import managerFactory
from SCanalyzer.gtfs_edit import edit_double

from geopy.geocoders import GoogleV3, Nominatim
from SCanalyzer.busSim.manager import LocalManager

from SCanalyzer.util import findEPSG
from pyproj import Transformer

def get_yelp_api_key():
    with open("../config.yml", 'r') as yml:
        cfg = yaml.safe_load(yml)
        return cfg["yelp"]["api_key"]

def plot_background(crs):
    background_path = os.path.join('..', 'data', 'plot', 'background')
    city = gpd.read_file(os.path.join(background_path, "madison-meter-shp")).to_crs(crs)
    lakes = gpd.read_file(os.path.join(background_path, "water-meter-shp")).to_crs(crs)
    street = gpd.read_file(os.path.join(background_path, "street-meter-shp")).to_crs(crs)
    # city = gpd.read_file(background_path + "madison-shp")
    # lakes = gpd.read_file(background_path + "water-shp")
    # street = gpd.read_file(background_path + "street-shp")

    ax = city.plot(color="lightgray", alpha=.2, figsize=(12, 12), zorder=2)
    lakes.plot(color="lightblue", ax=ax, zorder=1, alpha=0.8)
    street.plot(color="darkgray", alpha = .5, ax=ax, zorder=3)
    return ax

api_key = 'ZsHZFGtKEZeOOXhTne98eErmfd6BfNTm9GqO2S6inSnWzDwtgC2sEauXcB-8zUna_lXZEal4jsW_St6O0OQOcuNvifrr6uqNYmjFXW-FyVKvaMyczbihWELI80tjYHYx'
gtfo = SCanalyzer(os.path.join('..', 'data', 'mmt_gtfs.zip'))
census_gdf = gtfo.load_census()
services_gdf = gtfo.load_yelp(api_key=api_key)


epsg = findEPSG(services_gdf['latitude'][0], services_gdf['longitude'][0])
transformer = Transformer.from_crs(4326, epsg)
stop_x, stop_y = transformer.transform(
            services_gdf['latitude'], services_gdf['longitude'])
services_gdf['stop_x'], services_gdf['stop_y'] = stop_x, stop_y
gdf = gpd.GeoDataFrame(
    geometry=gpd.points_from_xy(services_gdf.stop_x, services_gdf.stop_y), crs="EPSG:"+str(epsg))
gdf.plot()

# gtfo = SCanalyzer(os.path.join('..', 'data', 'mmt_gtfs.zip'))
# ax = plot_background(f"EPSG:{gtfo.epsg}")
# gtfo.set_batch_label(f"80-rm")
# example_gdf = gtfo.load_result_map(map_identifier="search-result-0-360!4")
# example_gdf.plot(color="#ffbfba", ax=ax)



# DATA_PATH = "../data/loop_gtfs_young.zip"
# OUT_PATH = "/tmp/output"
# DAY = "monday"
# START_TIME = "10:00:00"
# ELAPSE_TIME = "02:00:00"
# AVG_WALKING_SPEED = 1.4 # 1.4 meters per second
# MAX_WALKING_MIN = 12

# geolocator = Nominatim(user_agent="wisc_bazarr_demo")
# manager = LocalManager(DATA_PATH, OUT_PATH, None)
# busSim = BusSim(manager, DAY, START_TIME, ELAPSE_TIME, AVG_WALKING_SPEED, MAX_WALKING_MIN)

# cache = {}
# def geocode(addr):
#     if not "madison" in addr.lower():
#         addr += ", Madison WI"
#     if not addr in cache:
#         cache[addr] = geolocator.geocode(addr)
#     return cache[addr]

# leg_lines = []
# leg_text = []

# colors = ["orange", "blue", "green", "yellow"]

# zorder = 4
    
# bubbles = []
# addr = '330 N Orchard St'

# zorder += 10
# location = geocode(addr)
# lat, lon = (location.latitude, location.longitude)

# gdf = busSim.get_gdf(start_point=(lat, lon)) # draw bubble
# gdf = gdf.to_crs(epsg=4326)
