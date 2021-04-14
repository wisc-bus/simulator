import pandas as pd
from shapely.geometry import Point
from pyproj import Transformer
import geopandas as gpd

#import matplotlib.pyplot as plt
#import requests, json
#from mpl_toolkits.axes_grid1 import make_axes_locatable

class Census:
    """
    TODO
    """
    
    
    def __init__(self, gtfs_filename):
        """
        TODO
        """
        self.gtfs_file = gtfs_filename
     
        return 
    
    
    def getDemographicsMap(self):
        """
        TODO
        """
        
        return self.getCensusTracts()
    
    
    def getFarthestPoints(self, filename):
        """
        TODO
        """
        lat_lon_df = pd.read_csv(filename, usecols=['stop_lat', 'stop_lon'])
        
        # Convert latitude and longitude points to [Shaply] Point objects
        ID_points = [Point(
            lat_lon_df['stop_lon'][i], lat_lon_df['stop_lat'][i]) for i in range(len(lat_lon_df))]
        
        # Find the farthest (N, E, S, W) points of the system
        farthest_points = [ID_points[0] for i in range(4)]
        for point in ID_points:
            if point.y > farthest_points[0].y: # north = largest y (lat)
                farthest_points[0] = point
            if point.x > farthest_points[1].x: # east = largest x (lon)
                farthest_points[1] = point
            if point.y < farthest_points[2].y: # south = smallest y (lat)
                farthest_points[2] = point
            if point.x < farthest_points[3].x: # west = smallest x (lon)
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
        
        farthest_points = self.getFarthestPoints(self.gtfs_file)
        
        farthest_points_mercader = [self.coordinateTransform(point, old_epsg, new_epsg) for point in farthest_points]
        
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
    
        base_url = "https://tigerweb.geo.census.gov/arcgis/rest/services/TIGERweb/Tracts_Blocks/MapServer/11/query?"
        geometry = "geometry=" + str(round(center_lon, 2)) + "%2C" + str(round(center_lat, 2))
        mid_url = "&geometryType=esriGeometryPoint" + "&spatialRel=esriSpatialRelIntersects"
        distance = "&distance=" + str(round(max_sep, 2) + 2000) + "&units=esriSRUnit_Meter"
        end_url = ("&outFields=STATE%2CCOUNTY%2CTRACT%2CBLKGRP" + "&returnGeometry=true" + "&returnTrueCurves=false" +
                   "&returnIdsOnly=false" + "&returnCountOnly=false" + "&returnZ=false" + "&returnM=false" + 
                   "&returnDistinctValues=false" + "&returnExtentOnly=false" + "&featureEncoding=esriDefault" + 
                   "&f=geojson")

        url = base_url + geometry + mid_url + distance + end_url
        
        print("Getting geodataframe for tracts from Tigerweb...")
        geodataframe = gpd.read_file(url)
        
        return geodataframe
    
    
    
    def getDemographicsData(self, demographics=['Race'], demographicsDefaults=True):
        """"
        TODO
        if demographicsDefaults==True: then demographics should be a list of strings for demographis to return
        else: demographics should be a list of dictionaries specifying the codes from the census
        """
        
        Race = {'Total':'B02001_001E', 'White alone':'B02001_002E', 'Black or African American alone':'B02001_003E', 
            'American Indian and Alaska Native alone':'B02001_004E', 'Asian alone':'B02001_005E', 
            'Native Hawaiian and Other Pacific Islander alone':'B02001_006E'}
        
        
        return
    
    
    
    