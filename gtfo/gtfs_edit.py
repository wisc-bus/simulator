import zipfile, shutil, csv, io, itertools, sys
from collections import namedtuple

Trip = namedtuple("Trip", ["row", "stop_times"])

def edit_half(trips_hdr, stop_times_hdr, trips, trip_id_gen):
    trips_new = trips[::2]
    trips.clear()
    trips.extend(trips_new)

def copy_with_edits(path1, path2, edit_fn, route):
    with zipfile.ZipFile(path1) as zf1, zipfile.ZipFile(path2, "w") as zf2:
        # STEP 1: copy the files that don't get changed
        for info in zf1.infolist():
            if info.filename in ("trips.txt", "stop_times.txt"):
                continue
            with zf1.open(info.filename) as f1, zf2.open(info.filename, "w") as f2:
                shutil.copyfileobj(f1, f2)

        # STEP 2: separate trips that might get changed, copy trips that will not
        trips_changed = {} # key=trip_id, val=Trip object
        trips_unchanged = []
        max_trip_id = 0
        with zf1.open("trips.txt") as f:
            r = csv.reader(io.TextIOWrapper(f))
            trips_hdr = next(r)
            route_idx, trip_id_idx = trips_hdr.index("route_short_name"), trips_hdr.index("trip_id")
            for trip in r:
                trip_id = trip[trip_id_idx]
                if int(trip_id) > max_trip_id:
                    max_trip_id = int(trip_id)

                if int(trip[route_idx]) == int(route):
                    trips_changed[trip_id] = Trip(trip, [])
                else:
                    trips_unchanged.append(trip)

        with zf1.open("stop_times.txt") as f1, zf2.open("stop_times.txt", "w") as f2:
            # STEP 3: separate stop_times that might get changed, copy those that will not
            r = csv.reader(io.TextIOWrapper(f1))
            w = csv.writer(io.TextIOWrapper(f2, write_through=True))
            stimes_hdr = next(r)
            w.writerow(stimes_hdr)
            trip_id_idx = stimes_hdr.index("trip_id")

            for stime in r:
                trip_id = stime[trip_id_idx]
                if trip_id in trips_changed:
                    trips_changed[trip_id].stop_times.append(stime)
                else:
                    w.writerow(stime)

            # STEP 4: callback to determine edits
            trips_changed_lst = list(trips_changed.values())
            edit_fn(trips_hdr, stimes_hdr, trips_changed_lst,
                    itertools.count(max_trip_id+1))

            # STEP 5: copy over modified stop_times
            for trip in trips_changed_lst:
                for stime in trip.stop_times:
                    w.writerow(stime)

        # STEP 6: copy over modified trips
        with zf2.open("trips.txt", "w") as f:
            w = csv.writer(io.TextIOWrapper(f, write_through=True))
            w.writerow(trips_hdr)
            for trip in trips_unchanged:
                w.writerow(trip)
            for trip in trips_changed_lst:
                w.writerow(trip.row)

def main():
    if len(sys.argv) != 5:
        print("Usage: python3 gtfs_edit.py <orig-gtfs.zip> <new-gtfs.zip> <operation> <route>")
        print("Example: python3 gtfs_edit.py mmt_gtfs.zip out.zip half 80")
        sys.exit(1)

    path1, path2, op, route = sys.argv[1:]
    edit_fns = {"half": edit_half}
    if not op in edit_fns:
        print(f"{op} is not a valid operation.  Choose one of these:")
        print(",".join(sorted(edit_fns.keys())))
        sys.exit(1)

    copy_with_edits(path1, path2, edit_fns[op], route)

if __name__ == '__main__':
     main()
