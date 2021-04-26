import os, sys, json, zipfile, csv, shutil, io
from collections import namedtuple
from util import tomin, fmin
import pandas as pd
import matplotlib.pyplot as plt

Trip = namedtuple("Trip", ["service", "route", "direction"])

def main():
    if len(sys.argv) != 3:
        print("Usage: python3 gtfs_diff.py <zip1> <zip2>")
        sys.exit(1)

    dirsuffix = "-diff-temp-dir"
    zpaths = sys.argv[1:]
    tmpdirs = [zpath + dirsuffix for zpath in zpaths]

    # step 1: break trips into separate files by (service,route,direction)
    split_routes(zpaths, tmpdirs)

    # step 2: do a diff on each trip group
    diff_routes(zpaths, tmpdirs)

def split_routes(zpaths, tmpdirs):
    for zpath, tmpdir in zip(zpaths, tmpdirs):
        if os.path.exists(tmpdir):
            shutil.rmtree(tmpdir)
        os.mkdir(tmpdir)

        with zipfile.ZipFile(zpath) as zf:
            with zf.open("trips.txt") as f:
                trips = pd.read_csv(f)
                assert len(set(trips["trip_id"])) == len(trips)
            trips = {row.trip_id: Trip(str(row.service_id),
                                       str(row.route_short_name),
                                       str(row.direction_id))
                     for row in trips.itertuples()}

            curr_path = None
            curr_f = None
            curr_writer = None

            with zf.open("stop_times.txt") as f:
                r = csv.reader(io.TextIOWrapper(f))
                header = next(r)
                trip_id_idx = header.index("trip_id")
                for row in r:
                    trip_id = int(row[trip_id_idx])
                    trip = trips[trip_id]
                    this_path = os.path.join(tmpdir, "__".join(trip) + ".txt")
                    if this_path != curr_path:
                        if curr_f:
                            curr_f.close()
                        curr_path = this_path
                        is_new = not os.path.exists(curr_path)
                        curr_f = open(curr_path, "w" if is_new else "a")
                        curr_writer = csv.writer(curr_f)
                        if is_new:
                            curr_writer.writerow(header)
                    curr_writer.writerow(row)
            curr_f.close()

def diff_routes(zpaths, tmpdirs):
    names = []
    for d in tmpdirs:
        names.extend(os.listdir(d))
    names = sorted(set(names))
    for name in names:
        cumsum_trips = []
        for tdir in tmpdirs:
            path = os.path.join(tdir, name)
            if not os.path.exists(path):
                cumsum_trips.append(pd.Series())
            df = pd.read_csv(path)[["trip_id", "arrival_time"]]
            df["arrival_time"] = df["arrival_time"].apply(tomin)
            df.sort_values(by="arrival_time", inplace=True)
            df.drop_duplicates("trip_id", keep="first", inplace=True)
            cumsum_trips.append(df["arrival_time"].value_counts().sort_index().cumsum())

        # how many differ from the first one?
        diffs = 0
        for cumsum_trip in cumsum_trips[1:]
        if len(cumsum_trips[0]) == len(cumsum_trip):
            if (cumsum_trips[0].index == cumsum_trip.index).all():
                if (cumsum_trips[0] == cumsum_trip).all():
                    diff += 1

        # if at least one difference, plot it
        if diffs:
            print(name)
            fig, ax = plt.subplots()
            for zpath, version in zip(zpaths, cumsum_trips):
                version.plot.line(ax=ax, label=zpath)
            ax.legend()
            ax.set_xlabel("minutes into day")
            ax.set_ylabel("cumulative trips started")
            ax.get_figure().savefig(name.replace(".txt", ".svg"), format="svg", bbox_layout="tight")

if __name__ == '__main__':
     main()
