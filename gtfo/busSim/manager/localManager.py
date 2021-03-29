from .baseManager import BaseManager
import os
import pandas as pd
import geopandas as gpd


class LocalManager(BaseManager):
    def __init__(self, data_path, output_path):
        self.data_path = data_path
        self.output_path = output_path
        super().__init__()

    def read_csv(self, filename):
        path = os.path.join(self.data_path, "mmt_gtfs", filename)
        df = pd.read_csv(path, sep=",")
        return df

    def read_shape(self, filename):
        path = os.path.join(
            self.data_path, "plot", "background", filename)
        gdf = gpd.read_file(path)
        return gdf

    def save(self, result):
        with open(self.output_path, "wb") as f:
            f.write(result.to_bytes())
