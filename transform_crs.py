import pandas as pd
import geopandas as gpd
from pyproj import Transformer
import os


def transform_stop():
    stops_df = pd.read_csv("./data/mmt_gtfs/stops.csv", sep=",")
    transformer = Transformer.from_crs(4326, 3174)

    stop_x, stop_y = transformer.transform(
        stops_df["stop_lat"], stops_df["stop_lon"])
    stops_df["stop_x"] = stop_x
    stops_df["stop_y"] = stop_y
    stops_df.to_csv("./data/mmt_gtfs/stops-3174.csv")


def transform_lake():
    lakes = gpd.read_file("./data/plot/background/water-shp")
    lakes = lakes.to_crs(epsg=3174)

    if not os.path.exists('./data/plot/background/water-meter-shp'):
        os.makedirs('./data/plot/background/water-meter-shp')
    lakes.to_file("./data/plot/background/water-meter-shp/water-meter.shp")


if __name__ == "__main__":
    # transform_stop()
    transform_lake()
