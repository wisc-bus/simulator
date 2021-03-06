import pandas as pd
import geopandas as gpd
from busSim.graph import Graph
from busSim.util import dprint, transform, gen_start_time
from busSim.result import Result
import os
import time
import logging
from math import ceil, floor, sqrt


class BusSim:

    def __init__(
        self,
        data_path,
        day,
        start_time,
        elapse_time,
        avg_walking_speed=1.4,
        max_walking_min=-1,  # HACK
        route_remove=[],
        trip_delays=[]
    ):
        """The constructor of the BusSim class

        Args:
            data_path (str): The path to the directory of the data files
                (contains both mmt_gtfs and plot subdirectories)

            day (str): the day in a week to perform simulation on

            start_time (str): the starting time to perform simulation on
                (HH:MM:SS)

            elapse_time (str): the elapse time from starting time to perform
                simulation on (HH:MM:SS)

            avg_walking_speed (float): the assumed average walking speed

            max_walking_min (float): the maximum allowed walking time minutes

            route_remove (list[int], optional): the list
                of routes to remove

            trip_delays (list[Tuple], optional): the list
                of trip-delay pairs to add the tuple should be in the format of
                `(trip_id, delay in HH:MM:SS)`

        """
        self._logger = logging.getLogger('app')
        self._logger.info("Start initializing sim")
        self.data_path = data_path
        self.day = day
        self.start_time = start_time
        self.elapse_time = elapse_time
        self.avg_walking_speed = avg_walking_speed

        # HACK
        if max_walking_min == -1:
            max_walking_min = elapse_time
        self.max_walking_min = max_walking_min
        self.max_walking_distance = max_walking_min * 60.0 * avg_walking_speed
        self.stopTimes_final_df = self._gen_final_df(route_remove, trip_delays)
        self.graph = Graph(self.stopTimes_final_df, start_time,
                           elapse_time, self.max_walking_distance, avg_walking_speed)

        self._load_map()
        self._logger.info("Sim successfully initialized")

    @classmethod
    def run(cls, config):
        """Execute sim with route_ko from a config dict

        Here is an example of such config dict
        {
            "data_path": "PATH",
            "output_path": "PATH",
            "day": "monday",
            "start_time": "12:00:00",
            "elapse_time": 30, #min
            "start_points": [(43.073691, -89.387407)]
            "avg_walking_speed": 1.4, ##optional
            "max_walking_min": 10, #optional
            "grid_size_min": 2 #optional
        }
        """
        # check config dict
        required_fields = ["data_path", "output_path",  "day", "start_time",
                           "elapse_time", "start_points", "avg_walking_speed"]
        if not all(field in config for field in required_fields):
            raise Exception("Invalid config dict")
        if "max_walking_min" not in config:
            config["max_walking_min"] = config["elapse_time"]
        if "avg_walking_speed" not in config:
            config["avg_walking_speed"] = 1.4
        if "grid_size_min" not in config:
            config["grid_size_min"] = 2

        # init busSim
        busSim = cls(config["data_path"], config["day"], config["start_time"], config["elapse_time"],
                     config["avg_walking_speed"], config["max_walking_min"])
        config["x_num"], config["y_num"], _ = busSim._get_grid_dimention(
            config["grid_size_min"])
        result = Result(config)

        # run busSim search on every start_point
        for start_point in config["start_points"]:
            grid = busSim.get_access_grid(
                start_point=start_point, grid_size_min=config["grid_size_min"])
            result.record(start_point, grid)

        result.save(config["output_path"])

    def get_access_grid(self, start_stop=None, start_point=None, grid_size_min=2):
        x_num, y_num, grid_size = self._get_grid_dimention(grid_size_min)
        grid = []
        for y in range(y_num):
            row = []
            for x in range(x_num):
                row.append(0)
            grid.append(row)

        self._logger.info("Start searching graph")
        # first convert start_point into meters
        if start_point is not None:
            start_point = transform(start_point[0], start_point[1])
        stops_radius_list = self.graph.search(start_stop, start_point)

        if stops_radius_list is None or len(stops_radius_list) == 0:
            return grid

        self._logger.info("Start compressing")

        for bubble in stops_radius_list:
            min_x_idx = floor(
                (bubble["stop_x"] - self.min_x - bubble["radius"]) / grid_size)
            max_x_idx = floor(
                (bubble["stop_x"] - self.min_x + bubble["radius"]) / grid_size)
            min_y_idx = floor(
                (bubble["stop_y"] - self.min_y - bubble["radius"]) / grid_size)
            max_y_idx = floor(
                (bubble["stop_y"] - self.min_y + bubble["radius"]) / grid_size)

            # TODO: make this radius calculation more precise
            radius_idx = (max_x_idx - min_x_idx + 1) / 2
            mid_x_idx = (max_x_idx + min_x_idx) / 2
            mid_y_idx = (max_y_idx + min_y_idx) / 2

            for y in range(min_y_idx, max_y_idx+1):
                for x in range(min_x_idx, max_x_idx+1):
                    # check 4 corners, if the distance for all of them is greater than radius, then this grid is not in the circle
                    if (y - mid_y_idx) ** 2 + (x - mid_x_idx) ** 2 < radius_idx ** 2 or \
                        (y - mid_y_idx) ** 2 + (x + 1 - mid_x_idx) ** 2 < radius_idx ** 2 or \
                        (y + 1 - mid_y_idx) ** 2 + (x - mid_x_idx) ** 2 < radius_idx ** 2 or \
                            (y + 1 - mid_y_idx) ** 2 + (x + 1 - mid_x_idx) ** 2 < radius_idx ** 2:
                        grid[y][x] = 1

        self._logger.info("Finish generating grid")
        return grid

    def get_gdf(self, start_stop=None, start_point=None):
        """Given a starting point(lat, lon) or a starting stop_id, compute the region covered in geopandas.Geodataframe

        Args:
            start_stop (str, optional): The path to the directory of the data files
                (contains both mmt_gtfs and plot subdirectories)

            start_point (str, optional): the day in a week to perform simulation on

        Returns:
            geopandas.GeoDataFrame: the GeoDataFrame of the region covered

        """
        self._logger.info("Start searching graph")

        # first convert start_point into meters
        if start_point is not None:
            start_point = transform(start_point[0], start_point[1])
        stops_radius_list = self.graph.search(start_stop, start_point)

        if stops_radius_list is None or len(stops_radius_list) == 0:
            return

        self._logger.debug("start generating gdf")
        df = pd.DataFrame(stops_radius_list)

        gdf = gpd.GeoDataFrame(
            df, geometry=gpd.points_from_xy(df.stop_x, df.stop_y), crs="EPSG:3174")

        self._logger.debug("start generating geometry buffer with radius")
        gdf['geometry'] = gdf.geometry.buffer(gdf['radius'])
        self._logger.info("Finish generating gdf")
        return gdf

    def get_area(self, gdf):
        """This is a util method to compute the total area in meters^2 given a geopandas.Geodataframe

        Args:
            gdf (geopandas.GeoDataFrame): The Geodataframe used to compute the total area

        Returns:
            float: the total area in meters^2

        """
        if gdf is None:
            return

        # the area returned is in meters^2
        self._logger.info("start calculating area")

        self._logger.debug("start calculating union/difference")
        area = gdf.unary_union.difference(self.lakes.unary_union).area
        self._logger.info("finish calculating area")
        return area

    def _gen_final_df(self, route_remove, trip_delays):
        self._logger.debug("Start generating dataframe")

        mmt_gtfs_path = os.path.join(self.data_path, "mmt_gtfs")
        stops_df = pd.read_csv(os.path.join(
            mmt_gtfs_path, "stops-3174.csv"), sep=",")
        trips_df = pd.read_csv(os.path.join(
            mmt_gtfs_path, "trips.csv"), sep=",")
        stopTimes_df = pd.read_csv(os.path.join(
            mmt_gtfs_path, "stop_times.csv"), sep=",")
        calendar_df = pd.read_csv(os.path.join(
            mmt_gtfs_path, "calendar.csv"), sep=",")

        # get valid service_ids
        calendar_df['start_date'] = pd.to_datetime(
            calendar_df['start_date'], format='%Y%m%d')
        calendar_df['end_date'] = pd.to_datetime(
            calendar_df['end_date'], format='%Y%m%d')
        calendar_filtered_df = calendar_df[self._is_service_valid(
            calendar_df[self.day], calendar_df["service_id"])]
        service_ids = calendar_filtered_df["service_id"].tolist()

        # get valid trips
        trips_df = trips_df[trips_df["service_id"].isin(service_ids)]

        # remove routes
        trips_filtered_df = trips_df[~trips_df["route_short_name"].isin(
            route_remove)]

        # get valid stop_times
        stopTimes_filtered_df = trips_filtered_df.merge(
            stopTimes_df, on="trip_id")
        stopTimes_merged_df = stopTimes_filtered_df.merge(stops_df, on="stop_id")[
            ["service_id", "route_short_name", "trip_id", "stop_id", "stop_sequence", "arrival_time", "shape_dist_traveled", "stop_x", "stop_y", "cardinal_direction"]]

        # get stop_times within the time frame
        stopTimes_merged_df['arrival_time'] = pd.to_timedelta(
            stopTimes_merged_df['arrival_time'])

        # add trip_delays
        for (trip_id, delay) in trip_delays:
            stopTimes_merged_df.loc[stopTimes_merged_df["trip_id"]
                                    == trip_id, "arrival_time"] += pd.to_timedelta(delay)

        stopTimes_final_df = self._get_valid_stopTime(
            stopTimes_merged_df, self.start_time, self.elapse_time).sort_values(by="arrival_time")

        return stopTimes_final_df

    def _load_map(self):
        lake_path = os.path.join(
            self.data_path, "plot", "background", "water-meter-shp")
        city_path = os.path.join(
            self.data_path, "plot", "background", "madison-meter-shp")
        city = gpd.read_file(city_path)

        self.lakes = gpd.read_file(lake_path)
        self.max_x = city.bounds.maxx.max()
        self.min_x = city.bounds.minx.min()
        self.max_y = city.bounds.maxy.max()
        self.min_y = city.bounds.miny.min()

    def _is_service_valid(self, day, service_id):
        # FIXME: hardcode in the service to be 94
        return (day == 1) & (service_id.str.startswith("94"))

    def _get_valid_stopTime(self, df, start_time, elapse_time):
        start_time = pd.to_timedelta(start_time)
        end_time = start_time + pd.to_timedelta(elapse_time)
        return df[(df['arrival_time'] > start_time) & (df['arrival_time'] < end_time)]

    def _get_grid_dimention(self, grid_size_min):
        grid_size = grid_size_min * self.avg_walking_speed * 60
        x_num = ceil(abs(self.max_x - self.min_x) / grid_size)
        y_num = ceil(abs(self.max_y - self.min_y) / grid_size)
        return x_num, y_num, grid_size
