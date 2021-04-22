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

from pathlib import Path
import sys
import yaml
import time

import numpy as np
import geopandas as gpd
import matplotlib.pyplot as plt

DIR = Path('..')
sys.path.append(str(DIR))
from gtfo import Gtfo
from gtfo.busSim import BusSim, Config
from gtfo.busSim.manager import managerFactory


gtfo = Gtfo("../data/mmt_gtfs.zip")
census_gdf = gtfo.load_census()
services_gdf = gtfo.load_yelp(api_key=None)

routes = [80,  2, 70,  8, 10,  7,  4, 30,  6, 39, 84, 31,  5, 21, 17, 20, 15, 16, 18, 50, 40, 22, 26, 73, 67, 52, 13, 36, 32]
for route in routes:
    print(route)
    config = Config(day="monday", elapse_time="00:30:00", interval="06:10:00", max_walking_min=10, route_remove=[route])
    config.set_starts(centroids=census_gdf)
    result_gdf = gtfo.search(config)
    gtfo.add_service_metrics(result_gdf, services_gdf)
    gtfo.add_demographic_metrics(result_gdf, census_gdf)
    result_gdf.to_csv(f"../out/result{route}.csv", index=False)
    break
