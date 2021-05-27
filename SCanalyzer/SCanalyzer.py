from .busSim.manager import managerFactory
from .result.searchResult import SearchResult
from .util import transform
from .service.yelp import get_results
from .census import Census
import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.geometry import Polygon
from shapely.wkt import loads
from pyproj import Transformer
from zipfile import ZipFile
from io import TextIOWrapper
import os
from pathlib import Path
from math import ceil, floor
from collections import defaultdict
import time


class SCanalyzer:
    def __init__(self, gtfs_path):
        self.gtfs_path = gtfs_path
        self.base_out_path = self._get_out_path()
        self.out_path = self.base_out_path
        self._preprocess_gtfs()

    def set_batch_label(self, label):
        self.out_path = os.path.join(self.base_out_path, label)
        Path(self.out_path).mkdir(parents=True, exist_ok=True)

    def reset_batch_label(self):
        self.out_path = self.base_out_path

    def search(self, config, perf_df=None):
        # prerun check
        if not config.is_runnable():
            raise Exception("The current config is not runnable")

        # dynamically init a manager
        manager = managerFactory.create(
            config.get_run_env(), gtfs_path=self.gtfs_path, out_path=self.out_path, borders=self.borders)

        result_df = manager.run_batch(config, perf_df)

        return result_df

    def load_census(self, cache=True):
        """
        Looks for a stops.csv file in data/mmt_gtfs, queries TigerWeb Census API to pull out census tracts 
        based on the center and radius of the system. An optional addition of 1km (default) is added to the radius.
        From the tracts, and a default set of demographs the ACS 5-year 2019 dataset is queried to get the demographics
        data for each tract. A few statistics are computed. It returns a geodataframe with all of this information and
        saves it to the output folder. 

        cache     default=True, if true will load a saved result and return
        """

        # Pull from Cache and return:
        cache_path = os.path.join(self.base_out_path, "census.csv")
        if cache and os.path.exists(cache_path):
            census_df = pd.read_csv(cache_path)
            return self._csvdf_to_gdf(census_df)

        # Create the Geodataframe:
        c = Census(gtfs_filename="../data/mmt_gtfs/stops.csv")
        gdf_tracts = c.getCensusTracts()
        demographic_data = c.getDemographicsData(
            gdf_tracts, demographics=['Race', 'Vehicles'])

        # Save output:
        demographic_data.to_csv(cache_path, index=False)

        return self._csvdf_to_gdf(demographic_data)

    def load_yelp(self, api_key, services=["banks", "clinics", "dentists", "hospitals", "supermarket"], cache=True):
        cache_path = os.path.join(self.base_out_path, "services.csv")
        if cache and os.path.exists(cache_path):
            return pd.read_csv(cache_path)

        dfs = [get_results(api_key, service, self.borders)
               for service in services]
        df = pd.concat(dfs)
        df.to_csv(cache_path, index=False)
        return df

    def add_service_metrics(self, result_gdf, services_gdf, perf_df=None):
        # load grid size from a map_identifier (pick the first one on result_gdf)
        max_x, min_x, max_y, min_y, grid_size, x_num, y_num = self._load_grid_size(
            result_gdf)
        record_perf = (perf_df is not None)

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

        services_grid_series = services_gdf.groupby("service").apply(get_grid)
        services_counts = defaultdict(list)
        service_perfs = []

        # loop through all map_id in result_gdf
        # for records with the same filename: group open them and pull out each bitmaps
        curr_filename = None
        grid_iter = None
        for _, row in result_gdf.iterrows():
            s = time.time()
            filename, _ = self._parse_map_identifier(row["map_identifier"])

            # check if a new file need to be open
            if filename != curr_filename:
                curr_filename = filename
                grid_iter = SearchResult.grid_iter(filename)

            grid, _ = next(grid_iter, None)
            # combine bitmaps
            for service, servicemap in services_grid_series.items():
                services_counts[service].append(0)

            for y, grid_row in enumerate(grid):
                for x, bit in enumerate(grid_row):
                    if bit == 0:
                        continue

                    for service, servicemap in services_grid_series.items():
                        services_counts[service][-1] += servicemap[0][y][x]

            service_perfs.append(time.time() - s)

        for service, col in services_counts.items():
            result_gdf[service] = col

        if record_perf:
            perf_df["add_service_time"] = service_perfs

        return result_gdf

    def add_demographic_metrics(self, result_gdf, census_gdf, perf_df=None):
        max_x, min_x, max_y, min_y, grid_size, x_num, y_num = self._load_grid_size(
            result_gdf)
        record_perf = (perf_df is not None)

        # iterate through all the starting locations (only the unique starting locations)
        start_to_demographic_dict = {}
        for result_i, row in result_gdf.iterrows():
            s = time.time()
            _, i = self._parse_map_identifier(row["map_identifier"])
            if i not in start_to_demographic_dict:
                start_to_demographic_dict[i] = np.nan
                for census_i, census_row in census_gdf.iterrows():
                    if census_row["geometry"].contains(row["geometry"]):
                        start_to_demographic_dict[i] = census_i
                        break
            pop = np.nan
            cars = np.nan
            if not np.isnan(start_to_demographic_dict[i]):
                pop = census_gdf.at[start_to_demographic_dict[i], "Tot Pop"]
                cars = census_gdf.at[start_to_demographic_dict[i],
                                     "cars per capita"]
            result_gdf.at[result_i, "Tot Pop"] = pop
            result_gdf.at[result_i, "cars per capita"] = cars

            if record_perf:
                perf_df.at[result_i, "add_census_time"] = time.time() - s

        return result_gdf

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
        dir_path = Path().absolute()
        out_path = os.path.join(dir_path, "out")
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

    def _load_grid_size(self, result_gdf):
        map_identifier = result_gdf.at[0, "map_identifier"]
        filename, idx = self._parse_map_identifier(map_identifier)
        _, grid_size = SearchResult.load_grid(filename, idx)
        max_x, min_x, max_y, min_y = self.borders
        x_num = ceil(abs(max_x - min_x) / grid_size)
        y_num = ceil(abs(max_y - min_y) / grid_size)

        return max_x, min_x, max_y, min_y, grid_size, x_num, y_num

    def _csvdf_to_gdf(self, df):
        df['geometry'] = df['geometry'].apply(loads)
        gdf = gpd.GeoDataFrame(
            df, geometry="geometry", crs="EPSG:4326")
        return gdf
