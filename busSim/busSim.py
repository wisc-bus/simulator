import pandas as pd
import geopandas as gpd
from .graph import Graph
from .util import dprint, transform, gen_start_time
from .result import Result
from .fileManager import LocalManager, AWSManager
import logging
from math import ceil, floor, sqrt


class BusSim:

    def __init__(
        self,
        manager,
        day,
        start_time,
        elapse_time,
        avg_walking_speed=1.4,
        max_walking_min=-1,  # HACK
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

            trip_delays (list[Tuple], optional): the list
                of trip-delay pairs to add the tuple should be in the format of
                `(trip_id, delay in HH:MM:SS)`

        """
        self._logger = logging.getLogger('app')
        self._logger.info("Start initializing sim")
        self.manager = manager
        self.day = day
        self.start_time = start_time
        self.elapse_time = elapse_time
        self.avg_walking_speed = avg_walking_speed

        # HACK
        if max_walking_min == -1:
            max_walking_min = elapse_time
        self.max_walking_min = max_walking_min
        self.max_walking_distance = max_walking_min * 60.0 * avg_walking_speed
        self.stopTimes_final_df = self._gen_final_df(trip_delays)
        self.graph = Graph(self.stopTimes_final_df, start_time,
                           elapse_time, self.max_walking_distance, avg_walking_speed)

        self._load_map()
        self._logger.info("Sim successfully initialized")

    @classmethod
    def run(cls, config):
        """Execute sim with route_ko from a config dict

        Here is an example of such config dict
        {
            "run_env": {
                "backend": "local", # aws
                "credentials": {
                    "data_path": "PATH",
                    "output_path": "PATH",
                    "api_key": "YOUR_API_KEY" # required for aws
                }
            },
            "busSim_params": {
                "day": "monday",
                "start_time": "12:00:00",
                "elapse_time": 30, #min,
                "avg_walking_speed": 1.4, ##optional
                "max_walking_min": 10, #optional
                "grid_size_min": 2 #optional
            }, 
            "start_points": [(43.073691, -89.387407)],
            "route_remove": [80]
        }
        """
        # check config dict
        required_fields = ["run_env", "busSim_params",  "start_points"]
        if not all(field in config for field in required_fields):
            raise Exception("Invalid config dict")

        busSim_params = config["busSim_params"]
        if "max_walking_min" not in busSim_params:
            busSim_params["max_walking_min"] = busSim_params["elapse_time"]
        if "avg_walking_speed" not in busSim_params:
            busSim_params["avg_walking_speed"] = 1.4
        if "grid_size_min" not in busSim_params:
            busSim_params["grid_size_min"] = 2

        # TODO: make use of route_remove

        # dynamically init a manager
        backend = config["run_env"]["backend"]
        credentials = config["run_env"]["credentials"]
        managers = {
            "local": lambda: LocalManager(**credentials),
            "aws": lambda: AWSManager(**credentials)
        }
        if backend not in managers:
            raise Exception('Invalid Backend')
        manager = managers.get(backend)()

        # init busSim
        # TODO: use something like this busSim = cls(manager=manager, **busSim_params)
        busSim = cls(manager, busSim_params["day"], busSim_params["start_time"], busSim_params["elapse_time"],
                     busSim_params["avg_walking_speed"], busSim_params["max_walking_min"])

        busSim_params["x_num"], busSim_params["y_num"], _ = busSim._get_grid_dimention(
            busSim_params["grid_size_min"])
        result = Result(busSim_params)

        # run busSim search on every start_point
        for start_point in config["start_points"]:
            grid = busSim.get_access_grid(
                start_point=start_point, grid_size_min=busSim_params["grid_size_min"])
            result.record(start_point, grid)

        unique_routes = busSim.get_available_route()
        for route in config["route_remove"]:
            if route in unique_routes:
                for start_point in config["start_points"]:
                    grid = busSim.get_access_grid(
                        start_point=start_point, grid_size_min=busSim_params["grid_size_min"], route_remove=[route])
                    result.record(start_point, grid, route)
            else:
                result.record_batch(route)

        manager.save(result)

    def get_access_grid(self, start_stop=None, start_point=None, grid_size_min=2, route_remove=[]):
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
        stops_radius_list = self.graph.search(
            start_stop, start_point, route_remove)

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

    def get_gdf(self, start_stop=None, start_point=None, route_remove=[]):
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
        stops_radius_list = self.graph.search(
            start_stop, start_point, route_remove)

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

    def _gen_final_df(self, trip_delays):
        self._logger.debug("Start generating dataframe")

        stops_df = self.manager.read_csv("stops-3174.csv")
        trips_df = self.manager.read_csv("trips.csv")
        stopTimes_df = self.manager.read_csv("stop_times.csv")
        calendar_df = self.manager.read_csv("calendar.csv")

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

        # get valid stop_times
        stopTimes_filtered_df = trips_df.merge(
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

    def get_available_route(self):
        return self.stopTimes_final_df["route_short_name"].unique()

    def _load_map(self):
        city = self.manager.read_shape("madison-meter-shp")
        self.lakes = self.manager.read_shape("water-meter-shp")
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
