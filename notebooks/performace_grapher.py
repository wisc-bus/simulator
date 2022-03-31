from datetime import datetime
from pathlib import Path
import matplotlib.pyplot as plt
from time import time
import os, sys
from geopy.geocoders import GoogleV3, Nominatim
import geopandas as gpd
import pandas as pd
import matplotlib.dates as mdates

DIR = Path('..')
sys.path.insert(0, str(DIR))
from SCanalyzer import SCanalyzer
from SCanalyzer.busSim import BusSim
from SCanalyzer.busSim.manager import LocalManager

# make a graph of performance
def graph():
    pass

