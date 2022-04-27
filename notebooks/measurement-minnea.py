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
    start_points_dict = {'low': [(44.820852518773165, -93.27007526760357), (45.03698099490727, -93.3273018807822), (45.07520646479199, -93.36447314869748), (45.14351172737558, -93.26887266443758), (45.01564156164276, -93.37466650992579), (45.07391882519973, -93.26580601973103), (45.04092052687533, -93.26546083324378), (44.84429728444731, -93.24484777443656), (44.90964204554468, -93.4073130057834), (44.99941607025379, -93.05624081015259)], 'high': [(44.96694574782479, -93.27932464626308), (44.9908438111097, -93.24767264600557), (44.96096525625919, -93.24283547951629), (44.964202774732755, -93.2647555237972), (44.96872234263041, -93.25058726230623), (44.976190237605174, -93.25424267826821), (44.976190237605174, -93.25424267826821), (44.973751479498084, -93.27271856402542), (44.96872234263041, -93.25058726230623), (44.973751479498084, -93.27271856402542)]}
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
    
    DATA_PATH = "../data/minneapolist_gtfs.zip"
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
        for start_time in range(7,23,8):
            start_times.append('{} {:02}:{:02}:{:02}'.format(day, start_time, 0, 0))    
    runs.append(run(start_times, DATA_PATH, OUT_PATH, ELAPSE_TIME, AVG_WALKING_SPEED, MAX_WALKING_MIN, START_POINTS, START_LOCATIONS, crs))
    
    # with open("new_version2.json", "w") as f:
    #     json.dump(runs, f)
    print(pd.DataFrame(results).to_markdown())



if __name__ == '__main__':
    main()