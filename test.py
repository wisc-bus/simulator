# import geopandas as gpd
# import pandas as pd
# import matplotlib.pyplot as plt
# import numpy as np
# import json
# import time
# import os
# import sys
# from datetime import datetime, timedelta
# from shapely.geometry import Point
# from busSim import BusSim


# DATA_PATH = "./data"
# DAY = "monday"
# START_TIME = "12:00:00"
# ELAPSE_TIME = "00:10:00"
# AVG_WALKING_SPEED = 1.4  # 1.4 meters per second
# MAX_WALKING_MIN = 10


# def read_stop_ids():
#     ids = []

#     with open('stop_ids.txt', 'r') as f:
#         for line in f:
#             stop_id = int(line[:-1])
#             ids.append(stop_id)

#     return ids


# def gen_expected():
#     result = {}
#     stop_ids = read_stop_ids()
#     busSim = BusSim(DATA_PATH, DAY, START_TIME, ELAPSE_TIME,
#                     AVG_WALKING_SPEED, MAX_WALKING_MIN)
#     c = 0
#     for stop_id in stop_ids:
#         gdf = busSim.get_gdf(stop_id)
#         result[stop_id] = busSim.get_area(gdf)
#         c += 1
#         print(c)

#     with open('expected.json', 'w') as f:
#         json.dump(result, f)


# def run_test():
#     expected = {}
#     with open('expected.json', 'r') as f:
#         expected = json.load(f)

#     stop_ids = read_stop_ids()
#     busSim = BusSim(DATA_PATH, DAY, START_TIME, ELAPSE_TIME,
#                     AVG_WALKING_SPEED, MAX_WALKING_MIN)

#     c = 0
#     for stop_id in stop_ids:
#         gdf = busSim.get_gdf(stop_id)
#         assert expected[str(stop_id)] == busSim.get_area(gdf)
#         c += 1
#         print(c)


# if __name__ == "__main__":
#     # gen_expected()
#     run_test()

from gtfo import Gtfo
config = {
    "run_env": "local",
    "busSim_params": {
        "day": "monday",
        "elapse_time": "00:30:00",
        "avg_walking_speed": 1.4,
        "max_walking_min": 10,
        "grid_size_min": 2
    },
    "interval": "10:00:00",
    "start_points": [(43.073691, -89.387407)],
    "route_remove": [1, 10]
}

gtfo = Gtfo("./data/mmt_gtfs.zip",
            "./data/plot/background/madison-meter-shp", "/tmp")
search_result = gtfo.search(config)
