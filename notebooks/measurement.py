from datetime import datetime
from pathlib import Path
import matplotlib.pyplot as plt
from time import time
import os, sys
from geopy.geocoders import GoogleV3, Nominatim
import geopandas as gpd
import pandas as pd
from matplotlib.dates import DateFormatter

DIR = Path('..')
sys.path.insert(0, str(DIR))
from SCanalyzer import SCanalyzer
from SCanalyzer.busSim import BusSim
from SCanalyzer.busSim.manager import LocalManager

def flatten(s):
    return gpd.GeoDataFrame({"geometry": gpd.GeoSeries([s.unary_union])})

def gen_busSim(data_path=None, out_path=None, day=None, start_time=None, elapse_time=None, avg_walking_speed=None, max_walking_min=None):
    manager = LocalManager(data_path, out_path, None)
    busSim = BusSim(manager, day, start_time, elapse_time, avg_walking_speed, max_walking_min)
    return busSim

def get_area(start_point=None, start_location=None, busSim=None, crs=3174):
    
    if start_point != None:
        lat, lon = start_point
    else:
        geolocator = Nominatim(user_agent="area_demo")
        location = geolocator.geocode(start_location)
        lat, lon = (location.latitude, location.longitude)
    gdf = busSim.get_gdf(start_point=(lat, lon))
    if gdf is None:
        return 0
    gdf = gdf.to_crs(epsg=3174)
    bubble = flatten(gdf.geometry)
    return bubble.geometry.area/10**6

def draw_area_times(times,area, data_path):
    times = list(map(lambda x: datetime.strptime(x, "%H:%M:%S"), times))
    formatter = DateFormatter("%H:%M:%S")
    plt.gca().xaxis.set_major_formatter(formatter)
    plt.gcf().autofmt_xdate()
    plt.plot(times, area, label = "line 1")
    plt.xlabel('x - axis')
    plt.ylabel('y - axis')
    plt.title('area vs times')
    plt.legend()
    plt.savefig(data_path+'graph.png')

def main():
    # args: measurement.py arg1 arg2 arg3
    prog_start = time()
    if len(sys.argv) != 6:
        print('invalid args')
        return
    start_times = ['05:00:00',]
                    # '05:05:00',
                    # '05:10:00',
                    # '05:15:00',
                    # '05:20:00',
                    # '05:25:00',
                    # '05:30:00',
                    # '05:35:00',
                    # '05:40:00',
                    # '05:45:00',
                    # '05:50:00',
                    # '05:55:00',
                    # '06:00:00',
                    # '06:05:00',
                    # '06:10:00',
                    # '06:15:00',
                    # '06:20:00',
                    # '06:25:00',
                    # '06:30:00',
                    # '06:35:00',
                    # '06:40:00',
                    # '06:45:00',
                    # '06:50:00',
                    # '06:55:00',
                    # '07:00:00',]
    DATA_PATH = "../data/mmt_gtfs.zip" if sys.argv[1] == 'na' else sys.argv[1]
    OUT_PATH = "/tmp/output" if sys.argv[2] == 'na' else sys.argv[2]
    DAY = "monday" if sys.argv[3] == 'na' else sys.argv[3]
    sc = SCanalyzer(DATA_PATH)
    crs = sc.epsg

    # "330 N Orchard St, Madison WI"
    # "Minneapolis Institute of Art, Minneaplolis, MN"
    START_LOCATION = "330 N Orchard St, Madison WI" if sys.argv[4] == 'na' else sys.argv[4]
    # START_POINT = (44.980342, -93.264989) # minneapolis
    START_POINT = None
    ELAPSE_TIME = "01:50:00" if sys.argv[5] == 'na' else sys.argv[5]
    AVG_WALKING_SPEED = 1.4 # 1.4 meters per second
    MAX_WALKING_MIN = 12

    busSims = []
    for start_time in start_times:
        print('creat busSim')
        busSims.append(gen_busSim(DATA_PATH,OUT_PATH, DAY, start_time, ELAPSE_TIME, AVG_WALKING_SPEED, MAX_WALKING_MIN))

    areas = []
    for busSim in busSims:
        print('cal area')
        areas.append(get_area(start_point=START_POINT, start_location=START_LOCATION, busSim=busSim, crs=crs))
    
    print(f'{areas=}')
    draw_area_times(start_times, areas, DATA_PATH)
    duration = time() - prog_start
    print(f'time taken {duration}')
    

if __name__ == '__main__':
    main()