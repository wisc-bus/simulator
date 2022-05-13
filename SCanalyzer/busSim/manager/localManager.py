from .baseManager import BaseManager
from ..busSim import BusSim
from ...result.searchResult import SearchResult
import os
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
from zipfile import ZipFile
import time
from tqdm import tqdm

class LocalManager(BaseManager):
    def __init__(self, gtfs_path, out_path, borders):
        super().__init__(gtfs_path, borders)
        self.out_path = out_path

    def run_batch(self, config, perf_df=None):
        busSim_params = config.get_busSim_params()
        start_times = config.get_start_times()
        start_points = config.get_start_points()

        result_df = pd.DataFrame(columns=["geometry", "start_time", "map_identifier"])
        # print(perf_df)

        with tqdm(total=len(start_times) * len(start_points)) as progress_bar:
            idx = 0
            for start_time in start_times:
                s = time.time()
                busSim = BusSim(self, busSim_params["day"], start_time, busSim_params["elapse_time"],
                                busSim_params["avg_walking_speed"], busSim_params["max_walking_min"])
                result = SearchResult(busSim, busSim_params["grid_size_min"])
                filename = result.get_out_filename()
                amortized_init_time = (time.time() - s) / len(start_points)

                # run busSim search on every start_point
                for stop_idx, start_point in enumerate(start_points):
                    s = time.time()
                    grid = busSim.get_access_grid(
                        start_point=start_point,
                        grid_size_min=busSim_params["grid_size_min"],
                        route_remove=busSim_params["route_remove"])
                    result.record(start_point, grid)

                    point = Point(start_point[1], start_point[0])
                    result_df.loc[idx, "geometry"] = point
                    result_df.loc[idx, "start_time"] = start_time
                    result_df.loc[idx, "map_identifier"] = f"{filename}!{stop_idx}"

                    if perf_df is not None:
                        perf_df.loc[idx, "search_time"] = time.time() - s + amortized_init_time
                        perf_df.loc[idx, "geometry"] = point
                        perf_df.loc[idx, "start_time"] = start_time

                    idx += 1
                    progress_bar.update(1)

                self.save(result)

        return result_df

    def read_gtfs(self, filename):
        with ZipFile(self.gtfs_path) as zf:
            # print(zf.namelist())
            with zf.open(filename) as f:
                df = pd.read_csv(f, sep=",")
                return df

    def save(self, result):
        out_path = os.path.join(self.out_path, result.get_out_filename())
        with open(out_path, "wb") as f:
            f.write(result.to_bytes())
