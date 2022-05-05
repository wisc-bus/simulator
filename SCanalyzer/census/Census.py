import pandas as pd
from shapely.geometry import Point
from pyproj import Transformer
import geopandas as gpd
import requests
import json
from zipfile import ZipFile

class Census:
    """
    TODO
    """

    def __init__(self, gtfs_path):
        """
        TODO
        """
        self.gtfs_path = gtfs_path

    def getDemographicsMap(self):
        """
        TODO
        """

        return self.getCensusTracts()

    def getFarthestPoints(self):
        """
        returns (N, E, S, W) bounding rectangle of GTFS stops using lat/lon
        """
        with ZipFile(self.gtfs_path) as zf:
            with zf.open("stops.txt") as f:
                lat_lon_df = pd.read_csv(f, usecols=['stop_lat', 'stop_lon'])

        # Convert latitude and longitude points to [Shaply] Point objects
        ID_points = [Point(
            lat_lon_df['stop_lon'][i], lat_lon_df['stop_lat'][i]) for i in range(len(lat_lon_df))]

        # Find the farthest (N, E, S, W) points of the system
        farthest_points = [ID_points[0] for i in range(4)]
        for point in ID_points:
            if point.y > farthest_points[0].y:  # north = largest y (lat)
                farthest_points[0] = point
            if point.x > farthest_points[1].x:  # east = largest x (lon)
                farthest_points[1] = point
            if point.y < farthest_points[2].y:  # south = smallest y (lat)
                farthest_points[2] = point
            if point.x < farthest_points[3].x:  # west = smallest x (lon)
                farthest_points[3] = point

        return farthest_points

    def coordinateTransform(self, coordinate, old_epsg="epsg:4326", new_epsg="epsg:3857"):
        """
        TODO

        coordinate        list: shaply Point object
        old_epsg          string: old coordinate system, default = "epsg:4326", lat/lon
        new_epsg          string: new coordinate system, default = "epsg:3857", mercader special, meters
        returns           list: the transformed coordinates
        """

        transformer = Transformer.from_crs("epsg:4326", "epsg:3857")

        return transformer.transform(coordinate.y, coordinate.x)

    def getCensusTracts(self, additionalRadius=1000, old_epsg="epsg:4326", new_epsg="epsg:3857"):
        """"
        TODO
        """

        farthest_points = self.getFarthestPoints()

        farthest_points_mercader = [self.coordinateTransform(
            point, old_epsg, new_epsg) for point in farthest_points]

        center_lon = (farthest_points_mercader[3][0] +
                      abs(farthest_points_mercader[1][0] - farthest_points_mercader[3][0])/2)
        center_lat = (farthest_points_mercader[2][1] +
                      abs(farthest_points_mercader[0][1] - farthest_points_mercader[2][1])/2)
        max_sep = max(abs(farthest_points_mercader[1][0] - farthest_points_mercader[3][0])/2,
                      abs(farthest_points_mercader[0][1] - farthest_points_mercader[2][1])/2)

        center_lon = round(center_lon, 2)
        center_lat = round(center_lat, 2)
        max_sep = round(max_sep, 2)
        max_sep + additionalRadius

        # TODO: don't hardcode; make sure the geography matches the
        # one used for the ACS data REST API query
        base_url = "https://tigerweb.geo.census.gov/arcgis/rest/services/Generalized_ACS2019/Tracts_Blocks/MapServer/4/query?"
        geometry = "geometry=" + \
            str(round(center_lon, 2)) + "%2C" + str(round(center_lat, 2))
        mid_url = "&geometryType=esriGeometryPoint" + \
            "&spatialRel=esriSpatialRelIntersects"
        distance = "&distance=" + \
            str(round(max_sep, 2) + 2000) + "&units=esriSRUnit_Meter"
        end_url = ("&outFields=STATE%2CCOUNTY%2CTRACT%2CBLKGRP" + "&returnGeometry=true" + "&returnTrueCurves=false" +
                   "&returnIdsOnly=false" + "&returnCountOnly=false" + "&returnZ=false" + "&returnM=false" +
                   "&returnDistinctValues=false" + "&returnExtentOnly=false" + "&featureEncoding=esriDefault" +
                   "&f=geojson")

        url = base_url + geometry + mid_url + distance + end_url

        print(f"Getting geodataframe for tracts from Tigerweb:\n{url}")
        geodataframe = gpd.read_file(url)

        return geodataframe

    def getDemographicsData(self, CensusTracts, demographics=['Race'], demographicsDefaults=True, sample=False):
        """"
        TODO
        if demographicsDefaults==True: then demographics should be a list of strings for demographis to return
        else: demographics should be a list of dictionaries specifying the codes from the census
        """

        Race = {'Total': 'B02001_001E', 'White alone': 'B02001_002E', 'Black or African American alone': 'B02001_003E',
                'American Indian and Alaska Native alone': 'B02001_004E', 'Asian alone': 'B02001_005E',
                'Native Hawaiian and Other Pacific Islander alone': 'B02001_006E'}

        Vehicles = {'Total Vehicles': 'B25044_001E'}

        print(
            "Getting demographics data from Census.gov, this may take a couple minutes...")

        combined_data = []
        CensusTracts = CensusTracts[1500:]

        if sample:
            CensusTracts = CensusTracts[0:10]

        for row in CensusTracts.iterrows():
            state = row[1]['STATE']
            tract = row[1]['TRACT']
            county = row[1]['COUNTY']
            blockgroup = row[1]['BLKGRP']

            race_list = [Race[key] for key in Race]
            car_list = [Vehicles[key] for key in Vehicles]
            demographics = race_list + car_list
            demographics = ','.join(demographics)

            # TODO: better to query by tract
            url_acs = "https://api.census.gov/data/2019/acs/acs5?"
            url_demographic = "get=NAME," + str(demographics) + "&"
            url_location = ("for=block%20group:" + str(blockgroup) + "&in=state:" + str(state) +
                            "%20county:" + str(county) + "%20tract:" + str(tract))
            url = url_acs + url_demographic + url_location

            resp = requests.get(url)
            resp.raise_for_status()

            data = resp.json()

            if len(combined_data) == 0:
                combined_data.append(data[0])
            combined_data.append(data[1])

        combined_df = pd.DataFrame(combined_data[1:], columns=combined_data[0])
        combined_df.rename(columns={'tract': 'TRACT', 'state': 'STATE',
                                    'county': 'COUNTY', 'block group': 'BLKGRP'}, inplace=True)

        joined_df = CensusTracts.merge(
            combined_df, on=['TRACT', 'STATE', 'COUNTY', 'BLKGRP'])

        # Id the demographics are the defaults then the stats will be computed and added to the geodataframe,
        # if it is not default then the user will have to compute them after the gdf is returned but before it
        # is combined with the results from the simulator
        if demographicsDefaults:

            joined_df['Tot Pop'] = joined_df['B02001_001E'].astype(int)
            joined_df['% White alone'] = (joined_df['B02001_002E'].astype(
                int) / joined_df['B02001_001E'].astype(int))
            joined_df['% Black or African American alone'] = (joined_df['B02001_003E'].astype(int) /
                                                              joined_df['B02001_001E'].astype(int))
            joined_df['% American Indian and Alaska Native alone'] = (joined_df['B02001_004E'].astype(int) /
                                                                      joined_df['B02001_001E'].astype(int))
            joined_df['% Asian alone alone'] = (joined_df['B02001_005E'].astype(int) /
                                                joined_df['B02001_001E'].astype(int))
            joined_df['% Native Hawaiian and Other Pacific Islander alone'] = (joined_df['B02001_006E'].astype(int) /
                                                                               joined_df['B02001_001E'].astype(int))

            joined_df['cars per capita'] = (joined_df['B25044_001E'].astype(
                int) / joined_df['B02001_001E'].astype(int))

        return joined_df
