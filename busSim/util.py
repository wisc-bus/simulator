import pandas as pd
from datetime import datetime
from pyproj import CRS, Transformer

# for quick debugging
debug = True


def dprint(cmd):
    if debug:
        print(cmd)


# for parsing perf logs
def parse_log_line(line):
    line = line.strip()
    tokens = line.split(" - ")
    timestamp = datetime.strptime(tokens[0], "%Y-%m-%d %H:%M:%S,%f")
    level = tokens[1]
    msg = tokens[2]
    return timestamp, level, msg


def to_millisecs(timedelta):
    return timedelta.total_seconds() * 1000


def get_perf(log_path):

    perf = pd.DataFrame()
    graph_search = projections = uninioning = None
    graph_search_ts = projections_ts = uninioning_ts = None
    i = 0

    with open(log_path) as f:
        for line in f:
            timestamp, level, msg = parse_log_line(line)

            if msg == "Start searching graph":
                # print(1)
                graph_search_ts = timestamp
            elif msg == "start generating gdf":
                # print(2)
                projections_ts = timestamp
                graph_search = projections_ts - graph_search_ts
            elif msg == "start calculating union/difference":
                # print(3)
                uninioning_ts = timestamp
                projections = uninioning_ts - projections_ts
            elif msg == "finish calculating area":
                # print(4)
                uninioning = timestamp - uninioning_ts
                # flush all previous results
                perf.loc[i, "graph_search"] = to_millisecs(graph_search)
                perf.loc[i, "projections"] = to_millisecs(projections)
                perf.loc[i, "uninioning"] = to_millisecs(uninioning)
                graph_search = projections = uninioning = None
                graph_search_ts = projections_ts = uninioning_ts = None
                i += 1

    return perf


# for transforming CRS
_transformer = None


def transform(lat, lon):
    global _transformer
    if _transformer is None:
        _transformer = Transformer.from_crs(4326, 3174)
    return _transformer.transform(lat, lon)
