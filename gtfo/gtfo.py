from .busSim.manager import managerFactory
import pandas as pd
from pyproj import Transformer
from zipfile import ZipFile
from io import TextIOWrapper
import os
from .util import gen_start_time


class Gtfo:
    def __init__(self, gtfs_path, out_path):
        self.gtfs_path = gtfs_path
        self.out_path = out_path
        self._preprocess_gtfs()

    def search(self, config):
        # prerun check
        if not config.is_runnable():
            raise Exception("The current config is not runnable")

        # dynamically init a manager
        manager = managerFactory.create(
            config.get_run_env(), gtfs_path=self.gtfs_path, out_path=self.out_path, borders=self.borders)

        start_times = gen_start_time(
            config.get_interval(), config.get_busSim_params().get("elapse_time"))
        result_df = manager.run_batch(config.get_busSim_params(), start_times,
                                      config.get_start_points())
        return result_df

    def services(self):
        pass

    def census(self):
        pass

    def load_result_map(self, map_identifier):
        pass

    def _preprocess_gtfs(self):
        self._reproject_stops()
        self.borders = self._get_borders()

    def _reproject_stops(self):
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
                # TODO change this to a fake file wrapper
                stops_df.to_csv("stops-3174.txt")

        with ZipFile(self.gtfs_path, "a") as zf:
            zf.write('stops-3174.txt')
        os.remove('stops-3174.txt')

    def _get_borders(self):
        # TODO optimize
        # 1. combine with previous _reproject_stops to only open the file once
        # 2. these can be computed within one loop
        with ZipFile(self.gtfs_path) as zf:
            with zf.open("stops-3174.txt") as f:
                stops_df = pd.read_csv(TextIOWrapper(f), sep=",")
                max_x = stops_df["stop_x"].max()
                min_x = stops_df["stop_x"].min()
                max_y = stops_df["stop_y"].max()
                min_y = stops_df["stop_y"].min()

                return (max_x, min_x, max_y, min_y)
