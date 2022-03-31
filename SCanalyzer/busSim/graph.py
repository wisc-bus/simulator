from datetime import timedelta
from math import sin, cos, asin, sqrt, pi, ceil, floor
from collections import defaultdict
import heapq
import pandas as pd
import geopandas as gpd
import logging

from time import time


class Node:
    def __init__(self, trip_id, route_short_name, stop_sequence, stop_id, stop_x, stop_y, arrival_time, max_walking_distance, node_id=-1):
        self.trip_id = trip_id
        self.route_short_name = route_short_name
        self.stop_sequence = stop_sequence
        self.stop_id = stop_id
        self.stop_x = stop_x
        self.stop_y = stop_y
        self.arrival_time = arrival_time
        # this should be modified by search in graph
        self.walking_distance = max_walking_distance
        self.children = []
        self.children_ids = set()
        self.id = node_id
        self.index = -1

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
        return f"({self.trip_id}, {self.route_short_name}, {self.stop_sequence}, {self.stop_id}, {self.arrival_time}, {self.walking_distance}"

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
        time0 = time()
        self._constuct_graph() # slow
        print(f'time cost for construct graph {time()-time0}sec')

        self._logger.debug(f"generated {len(self.nodes)} nodes in the graph")

    # return the area coverage data after performing graph search
    # return format: [{“stop_id”, “stop_y”, “stop_x”, “radius”}, ... ]
    def search(self, start_stop=None, start_point=None, route_remove=[]):
        if self.empty:
            return

        self._logger.debug("start locating starting stop") # fast
        start = self._find_start(start_stop, start_point) # fast
        self._logger.debug("start clearing graph") # fast
        self._clear_graph() # fast
        self._logger.debug("start runnning dijkstra") # fast
        time0 = time()

        self._dijkstra(start, route_remove) 
        print(f'time cost for dijkstra in graph search {time()- time0}sec')

        self._logger.debug("start collecting nodes") # fast
        stops_radius_dict = dict() # fast 
        start_time = pd.to_timedelta(self.start_time) # fast 
        end_time = start_time + pd.to_timedelta(self.elapse_time) # fast
        time0 = time()
        for node in self.nodes:
            # walking_distance = the distance between the prev node to current node
            if node.walking_distance < self.max_walking_distance:
                radius = self.max_walking_distance - node.walking_distance
                time_left = (end_time - node.arrival_time).total_seconds()
                # min(remaining walking distance based on maximum distance, remaining walking distance based on time left)
                radius = min(radius, self.avg_walking_speed * time_left)
                if node.stop_id not in stops_radius_dict or radius > stops_radius_dict[node.stop_id]["radius"]:
                    stops_radius_dict[node.stop_id] = {
                        "stop_id": node.stop_id,
                        "stop_x": node.stop_x,
                        "stop_y": node.stop_y,
                        "radius": radius
                    }
        print(f'time cost for generating radius loop in graph search {time()- time0}sec')

        stops_radius_list = [row for row in stops_radius_dict.values()]
        return stops_radius_list

    def _clear_graph(self):
        for node in self.nodes:
            node.walking_distance = self.max_walking_distance

    def _dijkstra(self, start, route_remove):
        pq = [(0, start)]
        builded_walk = set()
        while len(pq) > 0:
            curr_distance, curr_node = heapq.heappop(pq)
            # print(f"curr_distance: {curr_distance} curr_node: {curr_node}")

            # curr_node.walking_distance has only two cases: unchanged or smaller, because it only updates when getting smaller
            # curr_distance can be regarded as the previous value of curr_node.walking_distance
            if curr_distance > curr_node.walking_distance:
                continue
            
            # added by (Charles)
            if curr_node.id not in builded_walk:
                self._build_walk(curr_node)
                builded_walk.add(curr_node.id)

            for child in curr_node.children:
                if child.node.route_short_name in route_remove:
                    continue
                cost = child.cost # The distance between current node and parent node
                child = child.node

                distance = curr_distance + cost

                if distance < child.walking_distance:
                    child.walking_distance = distance
                    # if the current distance is shorter, we need to update all child nodes after the current node
                    heapq.heappush(pq, (distance, child))

    # new funciton
    def _build_walk(self, node):
        # print('build walk begin')
        time0 = time()
        index = node.index
        noLeft = False
        noRight = False
        length = len(self.nodes)
        range_len = length-index if index<length/2 else index+1 
        # print(f'node children len {len(node.children)}')
        for i in range(range_len):
            left_node = self.nodes[index-i] if index>= i and not noLeft else None
            right_node = self.nodes[index+i] if index<range_len-1 and not noRight else None

            noLeft = True if left_node==None or node.stop_x - left_node.stop_x>=self.max_walking_distance else False
            noRight = True if right_node==None or right_node.stop_x - node.stop_x>=self.max_walking_distance else False

            if noLeft and noRight:
                # print(f'building walk cost {time()-time0}')
                # print('return noleft and noright')
                # print(f'node children len after {len(node.children)}')
                return

            if not noLeft and left_node.id not in node.children_ids:
                distance_left = node.distance(left_node)
                time_delta_left = timedelta(seconds=(distance_left/self.avg_walking_speed))
                if distance_left < self.max_walking_distance and node.arrival_time+time_delta_left<left_node.arrival_time:
                    node.children.append(NodeCostPair(left_node, distance_left))
                    left_node.children.append(NodeCostPair(node,distance_left))
                    node.children_ids.add(left_node.id)
                    left_node.children_ids.add(node.id)

            if not noRight and right_node.id not in node.children_ids:
                distance_right = node.distance(right_node)
                time_delta_right = timedelta(seconds=(distance_right/self.avg_walking_speed))
                if distance_right < self.max_walking_distance and node.arrival_time+time_delta_right<right_node.arrival_time:
                    node.children.append(NodeCostPair(right_node, distance_right))
                    right_node.children.append(NodeCostPair(node,distance_right))
                    node.children_ids.add(right_node.id)
                    right_node.children_ids.add(node.id)
        print(f'building walk cost {time()-time0}')
            

    # new version
    def _constuct_graph(self):
        if len(self.df) == 0:
            self.empty = True
            return

        # gen nodes
        trip_node_dict = defaultdict(list)
        stop_node_dict = defaultdict(list)

        for index, row in self.df.iterrows():
            node = Node(row["trip_id"], row["route_id"], row["stop_sequence"], row["stop_id"], row["stop_x"],
                        row["stop_y"], row["arrival_time"], self.max_walking_distance, index)
            self.nodes.append(node)
            trip_node_dict[row["trip_id"]].append(node)
            stop_node_dict[row["stop_id"]].append(node)

        # gen edges
        # direct sequence
        # forms connection in each trip, with start being the first.
        for trip_id, nodes in trip_node_dict.items():
            for i in range(len(nodes)-1):
                start = nodes[i]
                end = nodes[i+1]
                nodeCostPair = NodeCostPair(end, 0)
                start.children.append(nodeCostPair)
                start.children_ids.add(end.id)

        # wait on stop: new version (by Charles)
        time0= time()
        for stop_id, nodes in stop_node_dict.items():
            for node in nodes:
                node.children.extend([NodeCostPair(n, 0) for n in filter(lambda n: n.arrival_time>node.arrival_time, nodes)])
        print(f'new time for reducted triple for loop {time() - time0}')

        # walk (Charles's version)
        time0 = time()
        self.nodes.sort(key=lambda node: node.stop_x)
        for index, node in enumerate(self.nodes):
            node.index = index
        time1 = time()
        print(f'time for sort nodes {time1-time0}')

    # OLDversion
    def _constuct_graph_old(self):
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

        # improvement? ok for now
        for i in range(x_num):
            x_list = []
            for j in range(y_num):
                x_list.append([])
            map_grid.append(x_list)

        for index, row in self.df.iterrows():
            node = Node(row["trip_id"], row["route_id"], row["stop_sequence"], row["stop_id"], row["stop_x"],
                        row["stop_y"], row["arrival_time"], self.max_walking_distance, index)
            self.nodes.append(node)
            trip_node_dict[row["trip_id"]].append(node)
            stop_node_dict[row["stop_id"]].append(node)

            # finding where the node is on the map_grid
            x_bucket = floor((row["stop_x"] - min_x) /
                             self.max_walking_distance)
            y_bucket = floor((row["stop_y"] - min_y) /
                             self.max_walking_distance)
            map_grid[x_bucket][y_bucket].append(node)

        # gen edges
        # direct sequence
        # forms connection in each trip, with start being the first.
        for trip_id, nodes in trip_node_dict.items():
            for i in range(len(nodes)-1):
                start = nodes[i]
                end = nodes[i+1]
                nodeCostPair = NodeCostPair(end, 0)
                start.children.append(nodeCostPair)
                start.children_ids.add(end.id)

        # wait on the stop
        # form connection between same stops which are not the same trip by checking their arrival time
        time0=time()
        for stop_id, nodes in stop_node_dict.items():
            for i in range(len(nodes)):
                for j in range(len(nodes)):
                    start = nodes[i]
                    end = nodes[j]
                    if start.arrival_time < end.arrival_time:
                        nodeCostPair = NodeCostPair(end, 0)
                        start.children.append(nodeCostPair)
                        start.children_ids.add(end.id)
        print(f'time cost for first origin triple loop {time()-time0}')

        # walk 
        # add node that are reacheable through walking to its children
        for x in range(x_num):
            for y in range(y_num):
                start_bucket = map_grid[x][y]
                end_buckets = []
                # following should be linear time, since x range and y range is fixed to most at 3
                for x_end in range(max(0, x-1), min(x_num, x+2)):
                    for y_end in range(max(0, y-1), min(y_num, y+2)):
                        end_buckets.append(map_grid[x_end][y_end])

                for start in start_bucket:
                    for end_bucket in end_buckets:
                        for end in end_bucket:
                            if start.arrival_time >= end.arrival_time or start.stop_id == end.stop_id:
                                continue

                            # walk
                            distance = start.distance(end)
                            time_delta = distance / self.avg_walking_speed
                            time_delta = timedelta(seconds=time_delta)
                            if distance < self.max_walking_distance and start.arrival_time + time_delta < end.arrival_time:
                                nodeCostPair = NodeCostPair(end, distance)
                                start.children.append(nodeCostPair)
                                start.children_ids.add(end.id)

    def _find_neighbour_nodes(self, start_node, radius):
        self.nodes = sorted(self.nodes, key=lambda node: node.stop_x)


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
        start = Node(trip_id=None, route_short_name=None, stop_sequence=None, stop_id=None, stop_x=x, stop_y=y,
                     arrival_time=pd.to_timedelta(self.start_time), max_walking_distance=0)

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
                start.children_ids.add(end.id)

        return start
