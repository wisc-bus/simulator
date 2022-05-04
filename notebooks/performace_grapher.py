from datetime import datetime
from pathlib import Path
import matplotlib.pyplot as plt
from time import time
import os, sys, json
from geopy.geocoders import GoogleV3, Nominatim
import geopandas as gpd
import pandas as pd
import matplotlib.dates as mdates
import numpy as np

DIR = Path('..')
sys.path.insert(0, str(DIR))
from SCanalyzer import SCanalyzer
from SCanalyzer.busSim import BusSim
from SCanalyzer.busSim.manager import LocalManager

# make a graph of performance
def graph(X,Y):
    Y1 = Y["original_version"]
    Y2 = Y["new_version"]

    fig = plt.figure(figsize = (10, 5))
    X_axis = np.arange(len(X))
    # creating the bar plot
    plt.bar(X_axis-0.2, Y1, color ='orange',
            width = 0.4, label="original_version")
    plt.bar(X_axis+0.2, Y2, color ='lightblue',
            width = 0.4, label="new_version")
    plt.xticks(ticks=X_axis, labels=X, fontsize=14)
    plt.yticks(fontsize=14)
    plt.xlabel("Frequency", fontsize=18)
    plt.ylabel("Time (sec)", fontsize=18)
    plt.title("Time vs Frequency", fontsize=22)
    plt.legend()
    plt.savefig("perf_short.png", bbox_inches="tight")

# gets the x values, format: [x1, x2, x3...]
# gets the y values, format: {'original_version':[y11,y12,y13...], 'new_version':[y21,y22,y23...]}
def main():
    x = [3, 5, 9]
    y = {'new_version':[23.54348635673523, 17.449768543243408, 77.29141354560852],
         'original_version':[26.363208770751953, 18.625696420669556, 75.41746616363525]} 
    graph(x,y)

if __name__ == '__main__':
    main()
