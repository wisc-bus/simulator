import zipfile, shutil, csv, io, itertools, sys
from collections import namedtuple, defaultdict
from util import tomin, fmin

VERBOSE = True
Trip = namedtuple("Trip", ["row", "stop_times"])

def print_trips(trips_hdr, arrival_idx, trips):
    service_idx = trips_hdr.index("service_id")
    trip_id_idx = trips_hdr.index("trip_id")
    direction_id_idx = trips_hdr.index("direction_id")
    for trip in trips:
        times = [str(stime[arrival_idx]) for stime in trip.stop_times]
        print(f"TRIP({trip.row[service_idx]}, {trip.row[direction_id_idx]}, {trip.row[trip_id_idx]}): "
              + ", ".join(times[:8]) + " (min since day start)...")
    print(f"TOTAL TRIPS: {len(trips)}")

def copy_trip(trip1, trip2_start, arrival_idx, departure_idx):
    min_inc = trip2_start - trip1.stop_times[0][arrival_idx]
    trip2 = Trip(row=trip1.row.copy(), stop_times=[])
    for stime1 in trip1.stop_times:
        stime2 = stime1.copy()
        stime2[arrival_idx] += min_inc
        stime2[departure_idx] += min_inc
        trip2.stop_times.append(stime2)
    return trip2

def set_trip_id(trip, trip_id, trip_id_idx, stop_times_trip_id_idx):
    trip.row[trip_id_idx] = trip_id
    for stime in trip.stop_times:
        stime[stop_times_trip_id_idx] = trip_id

def edit_double(trips_hdr, stop_times_hdr, trips, trip_id_gen):
    trip_id_idx = trips_hdr.index("trip_id")
    stop_times_trip_id_idx = stop_times_hdr.index("trip_id")
    service_idx = trips_hdr.index("service_id")
    route_idx = trips_hdr.index("route_short_name")
    direction_id_idx = trips_hdr.index("direction_id")
    arrival_idx = stop_times_hdr.index("arrival_time")
    departure_idx = stop_times_hdr.index("departure_time")

    # key: (service, route, direction), val: list of trips
    groups = defaultdict(list)
    for trip in trips:
        key = (trip.row[service_idx], trip.row[route_idx], trip.row[direction_id_idx])
        groups[key].append(trip)

    for group in groups.values():
        for i in range(len(group) - 1):
            trip_before = group[i]
            trip_after = group[i+1]
            new_start_time = (trip_before.stop_times[0][arrival_idx] +
                              trip_after.stop_times[0][arrival_idx]) // 2
            new_trip = copy_trip(trip_before, new_start_time,
                                 arrival_idx, departure_idx)
            set_trip_id(new_trip, next(trip_id_gen), trip_id_idx, stop_times_trip_id_idx)
            trips.append(new_trip)

def edit_half(trips_hdr, stop_times_hdr, trips, trip_id_gen):
    trips_new = trips[::2]
    trips.clear()
    trips.extend(trips_new)

def copy_with_edits(path1, path2, edit_fn, route):
    with zipfile.ZipFile(path1) as zf1, zipfile.ZipFile(path2, "w", compression=zipfile.ZIP_DEFLATED) as zf2:
        # STEP 1: copy the files that don't get changed
        for info in zf1.infolist():
            if not info.filename in ("trips.txt", "stop_times.txt"):
                with zf1.open(info.filename) as f1, zf2.open(info.filename, "w") as f2:
                    shutil.copyfileobj(f1, f2)

        # STEP 2: separate trips that might get changed, copy trips that will not
        trips_changed = {} # key=trip_id, val=Trip object
        trips_unchanged = []
        max_trip_id = 0
        with zf1.open("trips.txt") as f:
            r = csv.reader(io.TextIOWrapper(f))
            trips_hdr = next(r)
            service_idx = trips_hdr.index("service_id")
            route_idx = trips_hdr.index("route_short_name")
            direction_id_idx = trips_hdr.index("direction_id")
            trip_id_idx = trips_hdr.index("trip_id")
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
            arrival_idx = stimes_hdr.index("arrival_time")
            departure_idx = stimes_hdr.index("departure_time")

            for stime in r:
                trip_id = stime[trip_id_idx]
                if trip_id in trips_changed:
                    trips_changed[trip_id].stop_times.append(stime)
                else:
                    w.writerow(stime)

            # STEP 4: callback to determine edits
            
            # change times (str) to minutes (int) prior to edits
            trips_changed_lst = list(trips_changed.values())
            for trip in trips_changed_lst:
                for stime in trip.stop_times:
                    stime[arrival_idx] = tomin(stime[arrival_idx])
                    stime[departure_idx] = tomin(stime[departure_idx])
                trip.stop_times.sort(key=lambda stime: stime[arrival_idx])

            def sort_key(trip):
                return (trip.row[service_idx],
                        trip.row[route_idx],
                        trip.row[direction_id_idx],
                        trip.stop_times[0][arrival_idx])

            trips_changed_lst.sort(key=sort_key)
            if VERBOSE:
                print("BEFORE CHANGES:")
                print_trips(trips_hdr, arrival_idx, trips_changed_lst)

            # apply user-specified changes
            edit_fn(trips_hdr, stimes_hdr, trips_changed_lst,
                    itertools.count(max_trip_id+1))
            trips_changed_lst.sort(key=sort_key)

            if VERBOSE:
                print("\nAFTER CHANGES:")
                print_trips(trips_hdr, arrival_idx, trips_changed_lst)

            # change minutes (int) back to times (str)
            for trip in trips_changed_lst:
                for stime in trip.stop_times:
                    stime[arrival_idx] = fmin(stime[arrival_idx])
                    stime[departure_idx] = fmin(stime[departure_idx])

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
    edit_fns = {"half": edit_half, "double": edit_double}
    if not op in edit_fns:
        print(f"{op} is not a valid operation.  Choose one of these:")
        print(",".join(sorted(edit_fns.keys())))
        sys.exit(1)

    copy_with_edits(path1, path2, edit_fns[op], route)

if __name__ == '__main__':
     main()
