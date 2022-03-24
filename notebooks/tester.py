from pathlib import Path
import os, sys
from geopy.geocoders import GoogleV3, Nominatim
import geopandas as gpd
import pandas as pd
import matplotlib
import gtfs_kit as kit

DIR = Path('..')
sys.path.insert(0, str(DIR))
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
START_TIME = "04:55:00"
ELAPSE_TIME = "01:50:00"
start_location = "330 N Orchard St"

# Tina
DATA_PATH_2 = "../data/transfer_gtfs.zip"
START_TIME_2 = "12:58:47"
ELAPSE_TIME_2 = "00:59:00"
start_location_2 = "The Lux"

# Young
DATA_PATH_3 = "../data/loop_gtfs_young.zip"
START_TIME_3 = "10:00:00"
ELAPSE_TIME_3 = "02:00:00"

# Celia
DATA_PATH_4 = "../data/loop_gtfs.zip"
START_TIME_4 = "10:00:00"
ELAPSE_TIME_4 = "02:00:00"
start_location_4 = "sellery"

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

def get_area(start_point=None, start_location=None, busSim=None, crs=3174):
    location = geocode(start_location)
    lat, lon = (location.latitude, location.longitude)
    gdf = busSim.get_gdf(start_point=(lat, lon))
    gdf = gdf.to_crs(epsg=3174)
    bubble = flatten(gdf.geometry)
    return bubble.geometry.area

def get_error(path):
    feed = kit.feed.read_feed(path, dist_units='km')
    error=kit.validators.validate(feed, as_df=True, include_warnings=False)
    if len(error)==0:
        print("There's no error for the gtfs.")
    else:
        print("There's "+str(len(error))+" error for the gtfs.")
    return error

def test1():
    print("test1: check Charles' gtfs")
    area1 = get_area(start_location=start_location, busSim=gen_busSim())
    err = get_error(DATA_PATH)
    assert(len(err)!=0)

def test2():
    pass

def main():
    # use argument to detect validity of different city
    # Charles
    test1()
    
    # Tina
    print("check Tina's gtfs")
    area2 = get_area(start_location=start_location_2, busSim=gen_busSim(DATA_PATH_2, OUT_PATH, DAY, START_TIME_2, ELAPSE_TIME_2, AVG_WALKING_SPEED, MAX_WALKING_MIN))
    get_error(DATA_PATH_2)
    print(f'{area2=}')
    # Young
    print("check Young's gtfs")
    area3 = get_area(start_location=start_location, busSim=gen_busSim(DATA_PATH_3, OUT_PATH, DAY, START_TIME_3, ELAPSE_TIME_3, AVG_WALKING_SPEED, MAX_WALKING_MIN))
    get_error(DATA_PATH_3)
    print(f'{area3=}')
    # Celia
    print("check Celia's gtfs")
    area4 = get_area(start_location=start_location_4,busSim=gen_busSim(DATA_PATH_4,OUT_PATH,DAY, START_TIME_4, ELAPSE_TIME_4, AVG_WALKING_SPEED, MAX_WALKING_MIN))
    get_error(DATA_PATH_4)
    print(f'{area4=}')
                                   

if __name__ == '__main__':
    main()