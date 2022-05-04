from datetime import datetime
from pathlib import Path
import matplotlib.pyplot as plt
from time import time
import os, sys
from geopy.geocoders import GoogleV3, Nominatim
import geopandas as gpd
import pandas as pd
import matplotlib.dates as mdates
import json
from collections import OrderedDict
from numpy import median

DIR = Path('..')
sys.path.insert(0, str(DIR))
from SCanalyzer import SCanalyzer
from SCanalyzer.busSim import BusSim
from SCanalyzer.busSim.manager import LocalManager

global results

def flatten(s):
    return gpd.GeoDataFrame({"geometry": gpd.GeoSeries([s.unary_union])})

def gen_busSim(data_path=None, out_path=None, day=None, start_time=None, elapse_time=None, avg_walking_speed=None, max_walking_min=None):
    manager = LocalManager(data_path, out_path, None)
    busSim = BusSim(manager, day, start_time, elapse_time, avg_walking_speed, max_walking_min)
    return busSim

def get_area(start_points=[], start_locations=[], busSim=None, crs=3174):
    if len(start_points)==0:
        geolocator = Nominatim(user_agent="user_test")
        for loc in start_locations:
            location = geolocator.geocode(loc)
            print(location)
            start_point = (location.latitude, location.longitude)
            start_points.append(start_point)
    
    area_dict = {}
    # print(f'{start_points=}')
    for index, start in enumerate(start_points):
        print(f'{start=}')
        gdf = busSim.get_gdf(start_point=start)
        busSim.clear_graph()
        if gdf is None:
            area_dict[f'{start_points[index]}'] = 0
            continue
        gdf = gdf.to_crs(epsg=3174)
        bubble = flatten(gdf.geometry)
        area_dict[f'{start_points[index]}'] = bubble.geometry.area/10**6
    print(f'{area_dict=}')
    return area_dict

def draw_area_times(times, areas, data_path):
    global results
    fig, ax = plt.subplots(figsize=(12,8)) 
    times = list(map(lambda x: datetime.strptime(x.capitalize(), "%A %H:%M:%S  %d"), times))
    formatter = mdates.DateFormatter("%a %H:%M")
    plt.gca().xaxis.set_major_formatter(formatter)
    plt.gcf().autofmt_xdate()
    
    for key in areas.keys():
        print(f'loc {key}')
        print(f'{areas[key]=}')
        print(f'min value: {min(areas[key])}')
        results['min coverage'].append(min(areas[key]))
        results['max coverage'].append(max(areas[key]))
        results['median coverage'].append(median(areas[key]))
        print(f'max value: {max(areas[key])}')
        geoloctor = Nominatim(user_agent="reverse_user")
        info = geoloctor.reverse(key[1:-1]).raw
        if info != None:
            info = info['address']
            addr = ''
            for index, addrkey in enumerate(info):
                if index > 1:
                    break
                addr += " " + info[addrkey]
        else:
            addr = key
        ax.plot(times, areas[key], label = addr)
        results['label'].append(key)
    
    plt.xticks(fontsize=14)
    plt.yticks(fontsize=14)
    plt.xlabel('Time', fontsize=18)
    plt.ylabel("Area coverage "+ r'$(km^2)$', fontsize=18)
    plt.title('Area Coverage vs Time')
    plt.legend()
    plt.savefig('mearsurement_plot.png')

def run(start_times, DATA_PATH, OUT_PATH, ELAPSE_TIME, AVG_WALKING_SPEED, MAX_WALKING_MIN, START_POINTS, START_LOCATIONS, crs):
    global results
    prog_start = time()
    areas = {}
    for start_time in start_times:
        # print('creat busSim')
        day, start = start_time.split(' ')
        busSim = gen_busSim(DATA_PATH,OUT_PATH, day, start, ELAPSE_TIME, AVG_WALKING_SPEED, MAX_WALKING_MIN)
        # print('cal area')
        for key, area in get_area(start_points=START_POINTS, start_locations=START_LOCATIONS, busSim=busSim, crs=crs).items():
            if key not in areas:
                areas[key] = []
                areas[key].append(float(area))
            else:
                areas[key].append(float(area))
    # print(f'{areas=}')
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
    # results['time'].append(duration)
    print(f'time taken {duration}')
    return duration
    

def main():
    start_points_dict = {'low': [(43.05863684011441, -89.33164201625276), (43.1447167157741, -89.36849196981703), (43.13793231162969, -89.35904090074727), (43.10973220461785, -89.35378965001736), (43.11808048149292, -89.35926999648247), 
    (43.11808048149292, -89.35926999648247), (43.13793231162969, -89.35904090074727), (43.10973220461785, -89.35378965001736), (43.08965426447594, -89.51219979010558), (43.12035329229006, -89.36689904070965)], 
    'high': [(43.072651987610875, -89.39723842706803), (43.07057941738451, -89.40983549128191), (43.076773200791116, -89.38974345679428), (43.07497729569318, -89.40136555889757), (43.07057941738451, -89.40983549128191), (43.074180803910146, -89.38734526371564), (43.07157513303145, -89.38498094212332), (43.072651987610875, -89.39723842706803), (43.07916190274393, -89.38230221541342), (43.07916190274393, -89.38230221541342)]}
    global results
    results = {
        "label":[],
        "max coverage": [],
        "min coverage": [],
        "median coverage": []
    }

    print(f'{len(start_points_dict["high"])=}')
    START_POINTS = start_points_dict['high']
    # START_POINTS = []
    ELAPSE_TIME = "00:30:00"
    AVG_WALKING_SPEED = 1.4 # 1.4 meters per second
    MAX_WALKING_MIN = 12
    
    DATA_PATH = "../data/mmt_gtfs.zip"
    OUT_PATH = "/tmp/output" 
    sc = SCanalyzer(DATA_PATH)
    crs = sc.epsg
    START_LOCATIONS = []
    # START_LOCATIONS = ["330 N Orchard St, Madison", "The Nat, Madison", "Olbrich Gardens, Madison"]
    # START_LOCATIONS = ["Whispering Oaks, Minneapolis"]

    runs = []
    start_times = []
    # for day in ["monday"]:
    #     for start_time in range(5,24,6):
    #         start_times.append('{} {:02}:{:02}:{:02}'.format(day, start_time, 0, 0))    
    # runs.append(run(start_times, DATA_PATH, OUT_PATH, ELAPSE_TIME, AVG_WALKING_SPEED, MAX_WALKING_MIN, START_POINTS, START_LOCATIONS, crs))

    # start_times = []
    # for day in ["monday"]:
    #     for start_time in range(5,24,4):
    #         start_times.append('{} {:02}:{:02}:{:02}'.format(day, start_time, 0, 0))    
    # runs.append(run(start_times, DATA_PATH, OUT_PATH, ELAPSE_TIME, AVG_WALKING_SPEED, MAX_WALKING_MIN, START_POINTS, START_LOCATIONS, crs))

    # start_times = []
    days = ["monday", "tuesday", "wednesday", "thursday", "friday"]
    days = ["monday"]
    for day in days:
        for start_time in range(7,22,6):
            start_times.append('{} {:02}:{:02}:{:02}'.format(day, start_time, 0, 0))    
    runs.append(run(start_times, DATA_PATH, OUT_PATH, ELAPSE_TIME, AVG_WALKING_SPEED, MAX_WALKING_MIN, START_POINTS, START_LOCATIONS, crs))
    
    # with open("new_version2.json", "w") as f:
    #     json.dump(runs, f)
    print(pd.DataFrame(results).to_markdown())



if __name__ == '__main__':
    main()