from .busSim.manager import managerFactory
import pandas as pd
from pyproj import Transformer
from zipfile import ZipFile
from io import TextIOWrapper
import os
from .util import gen_start_time


class Gtfo:
    def __init__(self, gtfs_path, city_path, out_path):
        self.gtfs_path = gtfs_path
        self.city_path = city_path
        self.out_path = out_path
        self._preprocess_gtfs()

    def search(self, config):
        """Execute sim with route_ko from a config dict

        Here is an example of such config dict
        {
            "run_env": "local",
            "busSim_params": {
                "day": "monday",
                "elapse_time": "00:30:00",
                "avg_walking_speed": 1.4,
                "max_walking_min": 10,
                "grid_size_min": 2
            }, 
            "interval": "00:10:00",
            "start_points": [(43.073691, -89.387407)],
            "route_remove": [1, 10]
        }
        """
        print("Checking config obj")
        required_fields = ["run_env", "busSim_params",
                           "interval", "start_points", "route_remove"]
        if not all(field in config for field in required_fields):
            raise Exception("Invalid config dict")

        busSim_params = config["busSim_params"]
        if "avg_walking_speed" not in busSim_params:
            busSim_params["avg_walking_speed"] = 1.4
        if "max_walking_min" not in busSim_params:
            busSim_params["max_walking_min"] = busSim_params["elapse_time"]
        if "grid_size_min" not in busSim_params:
            busSim_params["grid_size_min"] = 2

        # dynamically init a manager
        manager = managerFactory.create(
            config["run_env"], gtfs_path=self.gtfs_path, city_path=self.city_path, out_path=self.out_path)

        start_times = gen_start_time(
            config["interval"], config["busSim_params"]["elapse_time"])
        for start_time in start_times:
            result = manager.run_batch(busSim_params, start_time,
                                       config["start_points"], config["route_remove"])
            manager.save(result)

    def services(self):
        pass

    def census(self):
        pass

    def _preprocess_gtfs(self):
        # reproject each stops into x, y
        with ZipFile(self.gtfs_path) as zf:
            if "stops-3174.txt" in zf.namelist():
                return
            with zf.open("stops.txt") as f:
                stops_df = pd.read_csv(TextIOWrapper(f), sep=",")
                transformer = Transformer.from_crs(4326, 3174)
                stop_x, stop_y = transformer.transform(
                    stops_df["stop_lat"], stops_df["stop_lon"])
                stops_df["stop_x"] = stop_x
                stops_df["stop_y"] = stop_y
                stops_df.to_csv("stops-3174.txt")

        with ZipFile(self.gtfs_path, "a") as zf:
            zf.write('stops-3174.txt')
        os.remove('stops-3174.txt')
