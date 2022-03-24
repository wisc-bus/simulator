from datetime import datetime
from pathlib import Path
import matplotlib.pyplot as plt
from time import time
import os, sys
from geopy.geocoders import GoogleV3, Nominatim
import geopandas as gpd
import pandas as pd
import matplotlib.dates as mdates

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

def get_area(start_points=[], start_locations=[], busSim=None, crs=3174):
    if len(start_points)==0:
        geolocator = Nominatim(user_agent="area_demo")
        for loc in start_locations:
            location = geolocator.geocode(loc)
            start_point = (location.latitude, location.longitude)
            start_points.append(start_point)
    
    area_dict = {}
    print(f'{start_points=}')
    for index, start in enumerate(start_points):
        print(f'{start=}')
        gdf = busSim.get_gdf(start_point=start)
        busSim.clear_graph()
        if gdf is None:
            area_dict[f'{start_locations[index]}'] = 0
            continue
        gdf = gdf.to_crs(epsg=3174)
        bubble = flatten(gdf.geometry)
        area_dict[f'{start_locations[index]}'] = bubble.geometry.area/10**6
    print(f'{area_dict=}')
    return area_dict

# def get_area(start_point=None, start_location=None, busSim=None, crs=3174):
#     if start_point != None:
#         lat, lon = start_point
#     else:
#         geolocator = Nominatim(user_agent="area_demo")
#         location = geolocator.geocode(start_location)
#         lat, lon = (location.latitude, location.longitude)
#     gdf = busSim.get_gdf(start_point=(lat, lon))
#     if gdf is None:
#         return 0
#     gdf = gdf.to_crs(epsg=3174)
#     bubble = flatten(gdf.geometry)
#     return bubble.geometry.area/10**6
def draw_area_times(times, areas, data_path):
    fig, ax = plt.subplots(figsize=(12,8)) 
    times = list(map(lambda x: datetime.strptime(x.capitalize(), "%A %H:%M:%S  %d"), times))
    formatter = mdates.DateFormatter("%a %H:%M")
    plt.gca().xaxis.set_major_formatter(formatter)
    plt.gcf().autofmt_xdate()
    
    for x in areas.keys():
        ax.plot(times, areas[x], label = x)
    
    plt.xlabel('times')
    plt.ylabel('area')
    plt.title('area vs times')
    plt.legend()
    plt.savefig(data_path+'graph2.png')



# times: list of tiem
# areas: {'start1':[point1, point2, point....], 'start2':[point1, point2, point....]}
# def draw_area_times(times,areas, data_path):
#     # print(f'{times}, {len(times)}')
#     # print(f'{areas=}, {len(areas)}')
#     times = list(map(lambda x: datetime.strptime(x.capitalize(), "%A %H:%M:%S  %d"), times))
#     print(f'{times=}')
#     formatter = mdates.DateFormatter("%a %H:%M")
#     plt.gca().xaxis.set_major_formatter(formatter)
#     plt.gcf().autofmt_xdate()
#     plt.plot(times, areas, label = "line 1")
#     plt.xlabel('x - axis')
#     plt.ylabel('y - axis')
#     plt.title('area vs times')
#     plt.legend()
#     plt.savefig(data_path+'graph.png')

def main():
    # args: measurement.py arg1 arg2 arg3
    prog_start = time()
    if len(sys.argv) != 6:
        print('invalid args')
        return
    # start_times = [ '05:00:00',
    #                 '06:00:00',
    #                 '07:00:00',
    #                 '08:00:00',
    #                 '09:00:00',
    #                 '10:00:00',
    #                 '11:00:00',
    #                 '12:00:00',
    #                 '13:00:00',
    #                 '14:00:00',
    #                 '15:00:00',
    #                 '16:00:00',
    #                 '17:00:00',
    #                 '18:00:00',
    #                 '19:00:00',
    #                 '20:00:00',
    #                 '21:00:00',
    #                 '22:00:00',
    #                 '23:00:00',]

    start_times = []
    for day in ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]:
        for start_time in range(6,24,6):
            start_times.append('{} {:02}:{:02}:{:02}'.format(day, start_time, 0, 0))
    DATA_PATH = "../data/stlouis_gtfs.zip" if sys.argv[1] == 'na' else sys.argv[1]
    OUT_PATH = "/tmp/output" if sys.argv[2] == 'na' else sys.argv[2]
    DAY = "monday" if sys.argv[3] == 'na' else sys.argv[3]
    sc = SCanalyzer(DATA_PATH)
    crs = sc.epsg

    # "330 N Orchard St, Madison WI"
    # "Minneapolis Institute of Art, Minneaplolis, MN"
    START_LOCATIONS = ["Busch Stadium", "Ranken Technical College", "Blackmon's Plaza"] if sys.argv[4] == 'na' else sys.argv[4]
    # START_POINT = (44.980342, -93.264989) # minneapolis
    START_POINTS = []
    ELAPSE_TIME = "00:30:00" if sys.argv[5] == 'na' else sys.argv[5]
    AVG_WALKING_SPEED = 1.4 # 1.4 meters per second
    MAX_WALKING_MIN = 12

    areas = {}
    for start_time in start_times:
        print('creat busSim')
        day, start = start_time.split(' ')
        busSim = gen_busSim(DATA_PATH,OUT_PATH, day, start, ELAPSE_TIME, AVG_WALKING_SPEED, MAX_WALKING_MIN)
        print('cal area')
        for key, area in get_area(start_points=START_POINTS, start_locations=START_LOCATIONS, busSim=busSim, crs=crs).items():
            if key not in areas:
                areas[key] = [area]
            else:
                areas[key].append(area)
         
    print(f'{areas=}')
    pre_day = ''
    day_index = 0
    for index in range(len(start_times)):
        day, start = start_times[index].split(' ')
        if pre_day != day:
            day_index+=1
            pre_day = day
        start_times[index] = f"{start_times[index]}  {day_index}"
        
    print(start_times)
    draw_area_times(start_times, areas, DATA_PATH)
    duration = time() - prog_start
    print(f'time taken {duration}')
    

if __name__ == '__main__':
    main()