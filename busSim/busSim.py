import pandas as pd
import geopandas as gpd
from busSim.graph import Graph
import os


class BusSim:

    def __init__(
        self,
        data_path,
        day,
        start_time,
        elapse_time,
        avg_walking_speed,
        max_walking_min,
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
        self.data_path = data_path
        self.day = day
        self.start_time = start_time
        self.elapse_time = elapse_time
        self.avg_walking_speed = avg_walking_speed
        self.max_walking_min = max_walking_min
        self.max_walking_distance = max_walking_min * 60.0 * avg_walking_speed
        self.stopTimes_final_df = self._gen_final_df(route_remove, trip_delays)
        self.graph = Graph(self.stopTimes_final_df, start_time,
                           elapse_time, self.max_walking_distance, avg_walking_speed)

    def get_gdf(self, start_stop=None, start_point=None):
        """Given a starting point(lat, lon) or a starting stop_id, compute the region covered in geopandas.Geodataframe

        Args:
            start_stop (str, optional): The path to the directory of the data files
                (contains both mmt_gtfs and plot subdirectories)

            start_point (str, optional): the day in a week to perform simulation on

        Returns:
            geopandas.GeoDataFrame: the GeoDataFrame of the region covered

        """
        gdf = self.graph.get_gdf(start_stop, start_point)
        if gdf is None:
            return

        gdf['geometry_centriod'] = gdf.geometry

        # https://epsg.io/3174
        gdf = gdf.to_crs(epsg=3174)
        gdf['geometry'] = gdf.geometry.buffer(gdf['radius'])
        gdf = gdf.to_crs(epsg=4326)
        return gdf

    def get_area(self, gdf):
        """This is a util method to compute the total area in meters^2 given a geopandas.Geodataframe

        Args:
            gdf (geopandas.GeoDataFrame): The Geodataframe used to compute the total area

        Returns:
            float: the total area in meters^2

        """
        # the area returned is in meters^2
        lake_path = os.path.join(
            self.data_path, "plot", "background", "water-shp")
        lakes = gpd.read_file(lake_path)
        lakes = lakes.to_crs(epsg=3174)
        gdf = gdf.to_crs(epsg=3174)
        return gdf.unary_union.difference(lakes.unary_union).area

    def _gen_final_df(self, route_remove, trip_delays):
        mmt_gtfs_path = os.path.join(self.data_path, "mmt_gtfs")
        stops_df = pd.read_csv(os.path.join(
            mmt_gtfs_path, "stops.csv"), sep=",")
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
            ["service_id", "route_short_name", "trip_id", "stop_id", "stop_sequence", "arrival_time", "shape_dist_traveled", "stop_lat", "stop_lon", "cardinal_direction"]]

        # get stop_times within the time frame
        stopTimes_merged_df.loc[(stopTimes_merged_df.arrival_time.str.startswith('24')), 'arrival_time'] = \
            stopTimes_merged_df.arrival_time.str.replace('24', '00')
        stopTimes_merged_df.loc[(stopTimes_merged_df.arrival_time.str.startswith('25')), 'arrival_time'] = \
            stopTimes_merged_df.arrival_time.str.replace('25', '01')
        stopTimes_merged_df.loc[(stopTimes_merged_df.arrival_time.str.startswith('26')), 'arrival_time'] = \
            stopTimes_merged_df.arrival_time.str.replace('26', '02')
        stopTimes_merged_df.loc[(stopTimes_merged_df.arrival_time.str.startswith('27')), 'arrival_time'] = \
            stopTimes_merged_df.arrival_time.str.replace('27', '03')
        stopTimes_merged_df.loc[(stopTimes_merged_df.arrival_time.str.startswith('28')), 'arrival_time'] = \
            stopTimes_merged_df.arrival_time.str.replace('28', '04')
        stopTimes_merged_df.loc[(stopTimes_merged_df.arrival_time.str.startswith('29')), 'arrival_time'] = \
            stopTimes_merged_df.arrival_time.str.replace('29', '05')
        stopTimes_merged_df['arrival_time'] = pd.to_timedelta(
            stopTimes_merged_df['arrival_time'])

        # add trip_delays
        for (trip_id, delay) in trip_delays:
            stopTimes_merged_df.loc[stopTimes_merged_df["trip_id"]
                                    == trip_id, "arrival_time"] += pd.to_timedelta(delay)

        stopTimes_final_df = self._get_valid_stopTime(
            stopTimes_merged_df, self.start_time, self.elapse_time).sort_values(by="arrival_time")

        return stopTimes_final_df

    def _is_service_valid(self, day, service_id):
        return (day == 1) & (service_id.str.startswith("94"))

    def _get_valid_stopTime(self, df, start_time, elapse_time):
        start_time = pd.to_timedelta(start_time)
        end_time = start_time + pd.to_timedelta(elapse_time)
        return df[(df['arrival_time'] > start_time) & (df['arrival_time'] < end_time)]
