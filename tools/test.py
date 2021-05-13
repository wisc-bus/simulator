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

DIR = Path('/Users/changxu/Desktop/projects/simulator/tools/..')
sys.path.append(str(DIR))
# print(sys.path)
from gtfo import Gtfo
from gtfo.busSim import BusSim, Config
from gtfo.busSim.manager import managerFactory


gtfo = Gtfo("./data/out.zip")
census_gdf = gtfo.load_census()
config = Config(day="monday", elapse_time="00:30:00", interval="10:30:00", max_walking_min=10)
# config.set_starts(points=[(43.073691, -89.387407), (43.073691, -89.387407)])
config.set_starts(centroids=census_gdf)
t0 = time.time()
result_gdf = gtfo.search(config)

result_gdf.get_access_grid(start_point=(43.02854678448197, -89.46876664203126)).sum()
