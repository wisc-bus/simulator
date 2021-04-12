from .busSim.manager import managerFactory
from .result.searchResult import SearchResult
from .util import gen_start_time, transform
from .service.yelp import get_results
import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.geometry import Polygon
from pyproj import Transformer
from zipfile import ZipFile
from io import TextIOWrapper
import os
from pathlib import Path
from math import ceil, floor


class Gtfo:
    def __init__(self, gtfs_path):
        self.gtfs_path = gtfs_path
        self.out_path = self._get_out_path()
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

    def load_yelp(self, api_key, services=["banks", "clinics", "dentists", "hospitals", "restaurants", "supermarket"]):
        services = ["banks", "clinics"]
        dfs = [get_results(api_key, service, self.borders)
               for service in services]
        return pd.concat(dfs)

    def add_service_metrics(self, result_gdf, services_gdf):
        # load grid size from a map_identifier (pick the first one on result_gdf)
        map_identifier = result_gdf.at[0, "map_identifier"]
        filename, idx = self._parse_map_identifier(map_identifier)
        _, grid_size = SearchResult.load_grid(filename, idx)
        max_x, min_x, max_y, min_y = self.borders
        x_num = ceil(abs(max_x - min_x) / grid_size)
        y_num = ceil(abs(max_y - min_y) / grid_size)

        def get_grid(df):
            grid = np.zeros(x_num*y_num).reshape(y_num, -1)
            for index, row in df.iterrows():
                # convert to 3174 first
                x, y = transform(row["latitude"], row["longitude"])
                x_idx = floor((x - min_x) / grid_size)
                y_idx = floor((y - min_y) / grid_size)
                if x_idx >= 0 and x_idx < x_num and y_idx >= 0 and y_idx < y_num:
                    grid[y_idx][x_idx] += 1

            return [grid]

        services_grid_df = services_gdf.groupby("service").apply(get_grid)
        return services_grid_df
        # for service, grid in grids.items():
        #     pass  # TODO: combine bitmaps here

    def load_result_map(self, map_identifier):
        filename, idx = self._parse_map_identifier(map_identifier)
        grid, grid_size = SearchResult.load_grid(filename, idx)
        max_x, min_x, max_y, min_y = self.borders

        # generate gdf
        df = pd.DataFrame(
            columns=["geometry"])
        i = 0
        for y, row in enumerate(grid):
            for x, bit in enumerate(row):
                x0 = grid_size * x + min_x
                x1 = x0 + grid_size
                y0 = grid_size * y + min_y
                y1 = y0 + grid_size
                if bit == 1:
                    df.loc[i, "geometry"] = Polygon(
                        [(x0, y0), (x0, y1), (x1, y1), (x1, y0)])
                    i += 1
        gdf = gpd.GeoDataFrame(df, crs="EPSG:3174")
        return gdf

    def _get_out_path(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        out_path = os.path.join(dir_path, os.pardir, "out")
        Path(out_path).mkdir(parents=True, exist_ok=True)
        return out_path

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
        # TODO: optimize
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

    def _parse_map_identifier(self, map_identifier):
        tokens = map_identifier.split("!")
        if len(tokens) != 2 or not tokens[1].isnumeric():
            raise Exception("invalid map_identifier")
        return os.path.join(self.out_path, tokens[0]), int(tokens[1])
