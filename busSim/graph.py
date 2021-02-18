from datetime import timedelta
from math import sin, cos, asin, sqrt, pi, ceil, floor
from collections import defaultdict
import heapq
import pandas as pd
import geopandas as gpd
import logging


class Node:
    def __init__(self, trip_id, stop_sequence, stop_id, stop_x, stop_y, arrival_time, max_walking_distance):
        self.trip_id = trip_id
        self.stop_sequence = stop_sequence
        self.stop_id = stop_id
        self.stop_x = stop_x
        self.stop_y = stop_y
        self.arrival_time = arrival_time
        # this should be modified by search in graph
        self.walking_distance = max_walking_distance
        self.children = []

    def distance(self, other):
        return sqrt((other.stop_x - self.stop_x)**2 + (other.stop_y - self.stop_y)**2)

    # Deprecated
    def harversine_distance(self, other):
        """Calculates the distance between two points on earth using the
        harversine distance (distance between points on a sphere)
        See: https://en.wikipedia.org/wiki/Haversine_formula

        :return: distance in meters between points
        """

        lat1, lon1, lat2, lon2 = (
            a/180*pi for a in [self.stop_lat, self.stop_lon, other.stop_lat, other.stop_lon])
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = sin(dlat/2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon/2) ** 2
        c = 2 * asin(min(1, sqrt(a)))
        d = 3956 * 1609.344 * c
        return d

    def __str__(self):
        return f"trip_id: {self.trip_id} stop_sequence: {self.stop_sequence} stop_id: {self.stop_id} stop_x: {self.stop_x} stop_y: {self.stop_y} arrival_time: {self.arrival_time} walking_distance: {self.walking_distance}"

    def __repr__(self):
        rv = self.__str__()
        rv += "\nChildren:\n"
        for child in self.children:
            rv += f"  cost: {child.cost} "
            child = child.node
            rv += str(child)
            rv += "\n"
        return rv

    def __lt__(self, other):
        # always retain sequence here
        return False


class NodeCostPair:
    def __init__(self, node, cost):
        self.node = node
        self.cost = cost  # the cost here means the walking distance


class Graph:
    def __init__(self, df, start_time, elapse_time, max_walking_distance, avg_walking_speed):
        self._logger = logging.getLogger('app')
        self._logger.debug("start generating graph")

        self.df = df
        self.start_time = start_time
        self.elapse_time = elapse_time
        self.max_walking_distance = max_walking_distance
        self.avg_walking_speed = avg_walking_speed
        self.nodes = []
        self.empty = False
        self._constuct_graph()

        self._logger.debug(f"generated {len(self.nodes)} nodes in the graph")

    # return the area coverage data after performing graph search
    # return format: [{“stop_id”, “stop_y”, “stop_x”, “radius”}, ... ]
    def search(self, start_stop=None, start_point=None):
        if self.empty:
            return

        self._logger.debug("start locating starting stop")
        start = self._find_start(start_stop, start_point)
        self._logger.debug("start clearing graph")
        self._clear_graph()
        self._logger.debug("start runnning dijkstra")
        self._dijkstra(start)

        self._logger.debug("start collecting nodes")
        stops_radius_dict = dict()
        start_time = pd.to_timedelta(self.start_time)
        end_time = start_time + pd.to_timedelta(self.elapse_time)
        for node in self.nodes:
            if node.walking_distance < self.max_walking_distance:
                radius = self.max_walking_distance - node.walking_distance
                time_left = (end_time - node.arrival_time).total_seconds()
                radius = min(radius, self.avg_walking_speed * time_left)
                if node.stop_id not in stops_radius_dict or radius > stops_radius_dict[node.stop_id]["radius"]:
                    stops_radius_dict[node.stop_id] = {
                        "stop_id": node.stop_id,
                        "stop_x": node.stop_x,
                        "stop_y": node.stop_y,
                        "radius": radius
                    }

        stops_radius_list = [row for row in stops_radius_dict.values()]
        return stops_radius_list

    def _clear_graph(self):
        for node in self.nodes:
            node.walking_distance = self.max_walking_distance

    def _dijkstra(self, start):
        pq = [(0, start)]
        while len(pq) > 0:
            curr_distance, curr_node = heapq.heappop(pq)

            if curr_distance > curr_node.walking_distance:
                continue

            for child in curr_node.children:
                cost = child.cost
                child = child.node

                distance = curr_distance + cost

                if distance < child.walking_distance:
                    child.walking_distance = distance
                    heapq.heappush(pq, (distance, child))

    def _constuct_graph(self):
        if len(self.df) == 0:
            self.empty = True
            return

        # gen nodes
        trip_node_dict = defaultdict(list)
        stop_node_dict = defaultdict(list)

        map_grid = []
        min_x = self.df.stop_x.min()
        max_x = self.df.stop_x.max()
        min_y = self.df.stop_y.min()
        max_y = self.df.stop_y.max()

        x_num = ceil((max_x - min_x) / self.max_walking_distance)
        y_num = ceil((max_y - min_y) / self.max_walking_distance)
        for i in range(x_num):
            x_list = []
            for j in range(y_num):
                x_list.append([])
            map_grid.append(x_list)

        for index, row in self.df.iterrows():
            node = Node(row["trip_id"], row["stop_sequence"], row["stop_id"], row["stop_x"],
                        row["stop_y"], row["arrival_time"], self.max_walking_distance)
            self.nodes.append(node)
            trip_node_dict[row["trip_id"]].append(node)
            stop_node_dict[row["stop_id"]].append(node)
            x_bucket = floor((row["stop_x"] - min_x) /
                             self.max_walking_distance)
            y_bucket = floor((row["stop_y"] - min_y) /
                             self.max_walking_distance)
            map_grid[x_bucket][y_bucket].append(node)

        # gen edges
        # direct sequence
        for trip_id, nodes in trip_node_dict.items():
            for i in range(len(nodes)-1):
                start = nodes[i]
                end = nodes[i+1]
                nodeCostPair = NodeCostPair(end, 0)
                start.children.append(nodeCostPair)

        # wait on the stop
        for stop_id, nodes in stop_node_dict.items():
            for i in range(len(nodes)):
                for j in range(i+1, len(nodes)):
                    start = nodes[i]
                    end = nodes[j]
                    nodeCostPair = NodeCostPair(end, 0)
                    start.children.append(nodeCostPair)

        # walk
        for x in range(x_num):
            for y in range(y_num):
                start_bucket = map_grid[x][y]
                end_buckets = []
                for x_end in range(max(0, x-1), min(x_num, x+2)):
                    for y_end in range(max(0, y-1), min(y_num, y+2)):
                        end_buckets.append(map_grid[x_end][y_end])

                for start in start_bucket:
                    for end_bucket in end_buckets:
                        for end in end_bucket:
                            if start.arrival_time >= end.arrival_time:
                                continue

                            # walk
                            distance = start.distance(end)
                            time_delta = distance / self.avg_walking_speed
                            time_delta = timedelta(seconds=time_delta)
                            if distance < self.max_walking_distance and start.arrival_time + time_delta < end.arrival_time:
                                nodeCostPair = NodeCostPair(end, distance)
                                start.children.append(nodeCostPair)

    def _find_start(self, start_stop, start_point):
        if start_stop is not None:
            return self._find_start_stop(start_stop)

        elif start_point is not None:
            return self._find_start_point(start_point)

    def _find_start_stop(self, start_stop):
        for node in self.nodes:
            if node.stop_id == start_stop:
                start_point = (node.stop_x, node.stop_y)
                return self._find_start_point(start_point)

    def _find_start_point(self, start_point):
        x, y = start_point
        start = Node(None, None, None, x, y,
                     pd.to_timedelta(self.start_time), 0)

        # gen edges by walking
        for end in self.nodes:
            # unreachable for sure (can't go back in time)
            if start.arrival_time >= end.arrival_time:
                continue

            # walk
            distance = start.distance(end)
            time_delta = distance / self.avg_walking_speed
            time_delta = timedelta(seconds=time_delta)
            if distance < self.max_walking_distance and start.arrival_time + time_delta < end.arrival_time:
                nodeCostPair = NodeCostPair(end, distance)
                start.children.append(nodeCostPair)

        return start
