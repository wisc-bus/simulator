import pandas as pd
import geopandas as gpd
import numpy as np
from .graph import Graph
from ..util import transform
import logging
from math import ceil, floor, sqrt
import math

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
        self._logger.info("Sim successfully initialized")

    def get_access_grid(self, start_stop=None, start_point=None, grid_size_min=2, route_remove=[]):
        max_x, min_x, max_y, min_y = self.manager.get_borders()
        x_num, y_num, grid_size = self._get_grid_dimention(grid_size_min)
        grid = np.zeros(x_num*y_num).reshape(y_num, -1)

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
                (bubble["stop_x"] - min_x - bubble["radius"]) / grid_size)
            max_x_idx = floor(
                 (bubble["stop_x"] - min_x + bubble["radius"]) / grid_size)
            min_y_idx = floor(
                (bubble["stop_y"] - min_y - bubble["radius"]) / grid_size)
            max_y_idx = floor(
                (bubble["stop_y"] - min_y + bubble["radius"]) / grid_size)

            # TODO: make this radius calculation more precise
            radius_idx = (max_x_idx - min_x_idx + 1) / 2
            mid_x_idx = (max_x_idx + min_x_idx) / 2
            mid_y_idx = (max_y_idx + min_y_idx) / 2

            start_y = max(0, min_y_idx)
            start_x = max(0, min_x_idx)
            end_y = min(max_y_idx+1, y_num)
            end_x = min(max_x_idx+1, x_num)

            for y in range(start_y, end_y):
                for x in range(start_x, end_x):
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
        start_latlon=start_point
        # first convert start_point into meters
        if start_point is not None:
            start_point = transform(start_point[0], start_point[1])
            stops_radius_list = self.graph.search(start_stop, start_point, route_remove)

        if stops_radius_list is None or len(stops_radius_list) == 0:
            return

        self._logger.debug("start generating gdf")
        df = pd.DataFrame(stops_radius_list)
        def getZones(lat, lon):
            if lat >= 72.0 and lat < 84.0:
                if lon >= 0.0 and lon < 9.0:
                    return 31
                if lon >= 9.0 and lon < 21.0:
                    return 33
                if lon >= 21.0 and lon < 33.0:
                    return 35
                if lon >= 33.0 and lon < 42.0:
                    return 37
            if lat >= 56 and lat < 64.0 and lon >= 3 and lon <= 12:
                return 32
            return math.floor((lon + 180) / 6) + 1

        def findEPSG(lat, lon) :
            zone = getZones(lat, lon)
            #zone = (math.floor((longitude + 180) / 6) ) + 1  # without special zones for Svalbard and Norway         
            epsg_code = 32600
            epsg_code += int(zone)
            if (lat< 0): # South
                epsg_code += 100    
            return epsg_code

        epsg=str(findEPSG(start_latlon[0],start_latlon[1]))
        gdf = gpd.GeoDataFrame(
            df, geometry=gpd.points_from_xy(df.stop_x, df.stop_y), crs="EPSG:"+epsg)
        #EPSG:3174
        self._logger.debug("start generating geometry buffer with radius")
        gdf['geometry'] = gdf.geometry.buffer(gdf['radius']) # draw bubble with the given radius
        self._logger.info("Finish generating gdf")
        return gdf

    # def get_area(self, gdf):
    #     """This is a util method to compute the total area in meters^2 given a geopandas.Geodataframe

    #     Args:
    #         gdf (geopandas.GeoDataFrame): The Geodataframe used to compute the total area

    #     Returns:
    #         float: the total area in meters^2

    #     """
    #     if gdf is None:
    #         return

    #     # the area returned is in meters^2
    #     self._logger.info("start calculating area")

    #     self._logger.debug("start calculating union/difference")
    #     area = gdf.unary_union.difference(self.lakes.unary_union).area
    #     self._logger.info("finish calculating area")
    #     return area

    def _gen_final_df(self, trip_delays):
        self._logger.debug("Start generating dataframe")

        stops_df = self.manager.read_gtfs("stops_meter.txt")
        # for i in range(len(stops_df)):
        #     x,y = transform(float(stops_df.iloc[i]['stop_lat']), float(stops_df.iloc[i]['stop_lon']))
        #     #print(f"lat = {float(stops_df.iloc[i]['stop_lat'])}, lon = {float(stops_df.iloc[i]['stop_lon'])}")
        #     #print(f'x = {x}, y = {y}')
        #     stops_df.at[i,'stop_x'] = x
        #     stops_df.at[i,'stop_y'] = y
        print(f'new Stops df {stops_df}')
        trips_df = self.manager.read_gtfs("trips.txt")
        stopTimes_df = self.manager.read_gtfs("stop_times.txt")
        calendar_df = self.manager.read_gtfs("calendar.txt")

        # get valid service_ids
        calendar_df['start_date'] = pd.to_datetime(
            calendar_df['start_date'], format='%Y%m%d')
        calendar_df['end_date'] = pd.to_datetime(
            calendar_df['end_date'], format='%Y%m%d')
#         calendar_filtered_df = calendar_df[self._is_service_valid(
#             calendar_df[self.day], calendar_df["service_id"])]
        calendar_filtered_df = calendar_df
        service_ids = calendar_filtered_df["service_id"].tolist()

        # get valid trips
        trips_df = trips_df[trips_df["service_id"].isin(service_ids)]

        # get valid stop_times
        stopTimes_filtered_df = trips_df.merge(
            stopTimes_df, on="trip_id")
#         stopTimes_merged_df = stopTimes_filtered_df.merge(stops_df, on="stop_id")[
#             ["service_id", "route_short_name", "trip_id", "stop_id", "stop_sequence", "arrival_time", "shape_dist_traveled", "stop_x", "stop_y", "cardinal_direction"]]
        stopTimes_merged_df = stopTimes_filtered_df.merge(stops_df, on="stop_id")[
            ["service_id", "trip_id", "route_id", "stop_id", "stop_sequence", "arrival_time", "stop_x", "stop_y"]]

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

    def _is_service_valid(self, day, service_id):
        # FIXME: hardcode in the service to be 95, just pick the first service id
        return (day == 1) #& (str(service_id).startswith("95"))

    def _get_valid_stopTime(self, df, start_time, elapse_time):
        start_time = pd.to_timedelta(start_time)
        end_time = start_time + pd.to_timedelta(elapse_time)
        return df[(df['arrival_time'] > start_time) & (df['arrival_time'] < end_time)]

    def _get_grid_dimention(self, grid_size_min):
        max_x, min_x, max_y, min_y = self.manager.get_borders()
        grid_size = grid_size_min * self.avg_walking_speed * 60
        x_num = ceil(abs(max_x - min_x) / grid_size)
        y_num = ceil(abs(max_y - min_y) / grid_size)
        return x_num, y_num, grid_size
