import math
from pathlib import Path
import os, sys
from geopy.geocoders import GoogleV3, Nominatim
import geopandas as gpd
import pandas as pd
import matplotlib
import gtfs_kit as kit

DIR = Path('..')
sys.path.insert(0, str(DIR))
from SCanalyzer import busSim
from SCanalyzer import SCanalyzer
from SCanalyzer.busSim import BusSim
from SCanalyzer.busSim.manager import LocalManager
from shapely.geometry import Point
from matplotlib.lines import Line2D

OUT_PATH = "/tmp/output"
DAY = "monday"
AVG_WALKING_SPEED = 1.4 # 1.4 meters per second
MAX_WALKING_MIN = 12
geolocator = Nominatim(user_agent="wisc_bazarr_demo")

# Charles
DATA_PATH = "mygtfs.zip"
# START_TIME = "04:55:00" # cant catch the first bus
START_TIME = "04:50:00" # can catch the first bus
ELAPSE_TIME = "02:50:00"
start_location = "330 N Orchard St"
gdf_1 = None
busSim_1 = None

# Tina
DATA_PATH_2 = "../data/transfer_gtfs.zip"
START_TIME_2 = "12:58:47"
ELAPSE_TIME_2 = "00:59:00"
start_location_2 = "The Lux"
gdf_2 = None
busSim_2 = None

# Young
DATA_PATH_3 = "../data/loop_gtfs_young.zip"
START_TIME_3 = "10:00:00"
ELAPSE_TIME_3 = "02:00:00"
gdf_3 = None
busSim_3 = None

# Celia
DATA_PATH_4 = "../data/loop_gtfs.zip"
START_TIME_4 = "10:00:00"
ELAPSE_TIME_4 = "02:00:00"
start_location_4 = "sellery"
gdf_4 = None
busSim_4 = None

cache = {}
def geocode(addr):
    if not "madison" in addr.lower():
        addr += ", Madison WI"
    if not addr in cache:
        cache[addr] = geolocator.geocode(addr)
    return cache[addr]

def flatten(s):
    return gpd.GeoDataFrame({"geometry": gpd.GeoSeries([s.unary_union])})

def gen_busSim(data_path=DATA_PATH, out_path=OUT_PATH, day=DAY, start_time=START_TIME, elapse_time=ELAPSE_TIME, avg_walking_speed=AVG_WALKING_SPEED, max_walking_min=MAX_WALKING_MIN):
    manager = LocalManager(data_path, out_path, None)
    busSim = BusSim(manager, day, start_time, elapse_time, avg_walking_speed, max_walking_min)
    return busSim

# def get_area(start_point=None, start_location=None, busSim=None, crs=3174):
#     location = geocode(start_location)
#     lat, lon = (location.latitude, location.longitude)
#     print(f'lat, lon: {lat, lon}')
#     gdf = busSim.get_gdf(start_point=(lat, lon))
#     gdf = gdf.to_crs(epsg=3174)
#     bubble = flatten(gdf.geometry)
#     return bubble.geometry.area[0]

def get_route(start_point=None, start_location=None, busSim=None):
    location = geocode(start_location)
    lat, lon = (location.latitude, location.longitude)
    print(f'lat, lon: {lat, lon}')
    gdf = busSim.get_gdf(start_point=(lat, lon))
    return gdf

def get_area(gdf=None, crs=3174):
    gdf = gdf.to_crs(epsg=crs)
    bubble = flatten(gdf.geometry)
    return bubble.geometry.area[0]


def get_stops_radius_list(busSim=None):
    return busSim.stops_radius_list

def get_error(path):
    feed = kit.feed.read_feed(path, dist_units='km')
    error=kit.validators.validate(feed, as_df=True, include_warnings=False)
    if len(error)==0:
        print("There's no error for the gtfs.")
    else:
        print("There's "+str(len(error))+" error for the gtfs.")
    return error

def test_gtfs_errors_for_Charles():
    err = get_error(DATA_PATH)
    assert len(err) == 0, "There're some errors on the gtfs."

def test_route_searching_for_Charles():
    global gdf_1, busSim_1
    busSim_1 = gen_busSim()
    gdf_1 = get_route(start_location=start_location, busSim=busSim_1)
    assert gdf_1 is not None, 'the route was not found'

# test for upper bound of area
def test_area_upper_bound_for_Charles():
    area = get_area(gdf=gdf_1)
    stops_radius_list = get_stops_radius_list(busSim=busSim_1)
    square_sum_radius = 0
    for radius_dict in stops_radius_list:
        radius = radius_dict['radius']
        square_sum_radius += radius ** 2
    area_upper_bound = math.pi * square_sum_radius
    assert 0 <= area <= area_upper_bound, 'Area out of range'

def test_gtfs_errors_for_Tina():
    err = get_error(DATA_PATH_2)
    assert len(err) == 0, "There're some errors on the gtfs."

def test_route_searching_for_Tina():
    global gdf_2, busSim_2
    busSim_2 = gen_busSim()
    gdf_2 = get_route(start_location=start_location, busSim=busSim_2)
    assert gdf_2 is not None, 'the route was not found'

# test for upper bound of area
def test_area_upper_bound_for_Tina():
    area = get_area(gdf=gdf_2)
    stops_radius_list = get_stops_radius_list(busSim=busSim_2)
    square_sum_radius = 0
    for radius_dict in stops_radius_list:
        radius = radius_dict['radius']
        square_sum_radius += radius ** 2
    area_upper_bound = math.pi * square_sum_radius
    assert 0 <= area <= area_upper_bound, 'Area out of range'

def test_gtfs_errors_for_Young():
    err = get_error(DATA_PATH_3)
    assert len(err) == 0, "There're some errors on the gtfs."

def test_route_searching_for_Young():
    global gdf_3, busSim_3
    busSim_3 = gen_busSim()
    gdf_3 = get_route(start_location=start_location, busSim=busSim_3)
    assert gdf_3 is not None, 'the route was not found'

# test for upper bound of area
def test_area_upper_bound_for_Young():
    area = get_area(gdf=gdf_3)
    stops_radius_list = get_stops_radius_list(busSim=busSim_3)
    square_sum_radius = 0
    for radius_dict in stops_radius_list:
        radius = radius_dict['radius']
        square_sum_radius += radius ** 2
    area_upper_bound = math.pi * square_sum_radius
    assert 0 <= area <= area_upper_bound, 'Area out of range'

def test_gtfs_errors_for_Celia():
    err = get_error(DATA_PATH_4)
    assert len(err) == 0, "There're some errors on the gtfs."
    assert gdf_4 is not None, 'the route was not found'

def test_route_searching_for_Celia():
    global gdf_4, busSim_4
    busSim_4 = gen_busSim()
    gdf_4 = get_route(start_location=start_location, busSim=busSim_4)

# test for upper bound of area
def test_area_upper_bound_for_Celia():
    area = get_area(gdf=gdf_4)
    stops_radius_list = get_stops_radius_list(busSim=busSim_4)
    square_sum_radius = 0
    for radius_dict in stops_radius_list:
        radius = radius_dict['radius']
        square_sum_radius += radius ** 2
    area_upper_bound = math.pi * square_sum_radius
    assert 0 <= area <= area_upper_bound, 'Area out of range'

def main():
    pass                      

if __name__ == '__main__':
    main()