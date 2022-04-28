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
        results['label'].append(key)
        print(f'max value: {max(areas[key])}')
        ax.plot(times, areas[key], label = key)
    
    plt.xlabel('times')
    plt.ylabel('area')
    plt.title('area vs times')
    plt.legend()
    plt.savefig(data_path+'graph2.png')

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
    start_points_dict = {'low': [(42.69552749899424, -84.59724385814187), (42.678903862848266, -84.59248159369493), (42.70093874047502, -84.5972371795897), (42.7007910840444, -84.5572856246274), (42.677790726888496, -84.57890510682235), 
    (42.69182814771287, -84.61354679022507), (42.68622809427853, -84.56495335422156), (42.67809941765349, -84.5682437067551), (42.71365682127145, -84.53426523200933), (42.70780457246975, -84.56169111850734)], 
    'high': [(42.70154967243691, -84.5492375391658), (42.70154967243691, -84.5492375391658), (42.7089628139353, -84.54494465393294), 
    (42.700336171040526, -84.54284497805143), (42.71004236075822, -84.40608454957669), (42.689978589189316, -84.54221142906732), (42.7650948183785, -84.49947250001442), (42.72571904933564, -84.45452833285272), (42.73088680199716, -84.47358345971233), (42.729934705198126, -84.46865888239998)]}
    global results
    results = {
        "label":[],
        "max coverage": [],
        "min coverage": []
    }

    print(f'{len(start_points_dict["high"])=}')
    START_POINTS = start_points_dict['high']
    # START_POINTS = []
    ELAPSE_TIME = "00:30:00"
    AVG_WALKING_SPEED = 1.4 # 1.4 meters per second
    MAX_WALKING_MIN = 12
    
    DATA_PATH = "../data/lansing_gtfs.zip"
    OUT_PATH = "/tmp/output" 
    DAY = "monday"
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
    for day in ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]:
        for start_time in range(0,24,6):
            start_times.append('{} {:02}:{:02}:{:02}'.format(day, start_time, 0, 0))    
    runs.append(run(start_times, DATA_PATH, OUT_PATH, ELAPSE_TIME, AVG_WALKING_SPEED, MAX_WALKING_MIN, START_POINTS, START_LOCATIONS, crs))
    
    # with open("new_version2.json", "w") as f:
    #     json.dump(runs, f)
    print(pd.DataFrame(results).to_markdown())



if __name__ == '__main__':
    main()