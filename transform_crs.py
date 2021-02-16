import pandas as pd
from pyproj import Transformer


def transform_stop():
    stops_df = pd.read_csv("./data/mmt_gtfs/stops.csv", sep=",")
    transformer = Transformer.from_crs(4326, 3174)

    stop_x, stop_y = transformer.transform(
        stops_df["stop_lat"], stops_df["stop_lon"])
    stops_df["stop_x"] = stop_x
    stops_df["stop_y"] = stop_y
    stops_df.to_csv("./data/mmt_gtfs/stops-3174.csv")


if __name__ == "__main__":
    transform_stop()
