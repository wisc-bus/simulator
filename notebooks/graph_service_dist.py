from fileinput import filename
import json
import pandas as pd
import geopandas as gp
import matplotlib
import gtfs_kit as kit
import sys, os
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter

def draw(fts, data_path, out_name):
    times = fts.reset_index()['datetime']
    areas = fts['service_distance']
    formatter = DateFormatter("%Y-%m-%d %H:%M:%S")
    plt.gca().xaxis.set_major_formatter(formatter)
    plt.gcf().autofmt_xdate()
    plt.plot(times, areas, label = "line 1")
    plt.xlabel('x - axis')
    plt.ylabel('y - axis')
    plt.title('area vs times')
    plt.legend()
    plt.savefig(out_name)


def main():
    file_name = sys.argv[1]
    out_name = sys.argv[2]
    feed = kit.feed.read_feed(file_name, dist_units='km').drop_invalid_columns().clean()
    first_week = feed.get_first_week()
    trip_stats = feed.compute_trip_stats()
    fts = feed.compute_feed_time_series(trip_stats, dates=first_week, freq="2H")
    draw(fts, data_path = file_name + '_line.png', out_name=out_name)

if __name__ == '__main__':
    main()