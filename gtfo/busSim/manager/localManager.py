from .baseManager import BaseManager
from ..busSim import BusSim
from ...result.searchResult import SearchResult
import os
import pandas as pd
import geopandas as gpd
from zipfile import ZipFile


class LocalManager(BaseManager):
    def __init__(self, gtfs_path, out_path, borders):
        self.out_path = out_path
        super().__init__(gtfs_path, borders)

    def run_batch(self, busSim_params, start_time, start_points, route_remove):
        # init busSim
        busSim = BusSim(self, busSim_params["day"], start_time, busSim_params["elapse_time"],
                        busSim_params["avg_walking_speed"], busSim_params["max_walking_min"])
        result = SearchResult(busSim, busSim_params["grid_size_min"])

        # run busSim search on every start_point
        for start_point in start_points:
            grid = busSim.get_access_grid(
                start_point=start_point, grid_size_min=busSim_params["grid_size_min"])
            result.record(start_point, grid)

        # run busSim search again with different route removed
        unique_routes = busSim.get_available_route()
        for route in route_remove:
            if route in unique_routes:
                for start_point in start_points:
                    grid = busSim.get_access_grid(
                        start_point=start_point, grid_size_min=busSim_params["grid_size_min"], route_remove=[route])
                    result.record(start_point, grid, route)
            else:
                result.record_batch(route)

        return result

    def read_gtfs(self, filename):
        with ZipFile(self.gtfs_path) as zf:
            with zf.open(filename) as f:
                df = pd.read_csv(f, sep=",")
                return df

    def save(self, result):
        out_path = os.path.join(self.out_path, result.get_out_filename())
        with open(out_path, "wb") as f:
            f.write(result.to_bytes())
