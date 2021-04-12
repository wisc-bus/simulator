import pandas as pd
#from shapely.geometry import Point
#from pyproj import Proj, transform
#import geopandas as gpd
#import matplotlib.pyplot as plt
#import requests, json
#from mpl_toolkits.axes_grid1 import make_axes_locatable

class Census:
    
    def __init__(self, gtfs_filename):
        
        self.gtfs_gdf = self.parseGTFS(gtfs_filename)
        
        
        return 
    
    
    def parseGTFS(self, filename):
        
        lat_lon_df = pd.read_csv(filename, usecols=['stop_lat', 'stop_lon'])
        
        return lat_lon_df