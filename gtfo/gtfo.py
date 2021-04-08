from .busSim.manager import managerFactory
from .result.searchResult import SearchResult
import pandas as pd
import geopandas as gpd
from shapely.geometry import Polygon
from pyproj import Transformer
from zipfile import ZipFile
from io import TextIOWrapper
import os
from pathlib import Path
from .util import gen_start_time


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

    def services(self):
        pass

    def census(self):
        pass

    def load_result_map(self, map_identifier):
        tokens = map_identifier.split("!")
        if len(tokens) != 2 or not tokens[1].isnumeric():
            raise Exception("invalid map_identifier")
        filename, idx = tokens[0], int(tokens[1])

        grid, grid_size = SearchResult.load_grid(filename, idx)

        # generate gdf
        max_x, min_x, max_y, min_y = self.borders
        df = pd.DataFrame(
            columns=["geometry"])
        grid_size = 2 * 1.4 * 60
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
