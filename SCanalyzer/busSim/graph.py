from datetime import timedelta
from math import sin, cos, asin, sqrt, pi, ceil, floor, radians, atan2
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

    def __str__(self):
        return f"({self.trip_id}, {self.route_short_name}, {self.stop_sequence}, {self.stop_id}, {self.arrival_time}, {self.walking_distance}, {self.stop_x}, {self.stop_y})"

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
        # print(f'time cost for construct graph {time()-time0}sec')

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
        # print(f'time cost for dijkstra in graph search {time()- time0}sec')

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
        # print(f'time cost for generating radius loop in graph search {time()- time0}sec')

        stops_radius_list = [row for row in stops_radius_dict.values()]
        return stops_radius_list

    def haversine(self, lat1, lon1, lat2, lon2):
        # Radius of Earth in meters
        R = 6371000
        
        # Convert latitude and longitude from degrees to radians
        dlat = radians(lat2 - lat1)
        dlon = radians(lon2 - lon1)
        lat1 = radians(lat1)
        lat2 = radians(lat2)
        
        # Haversine formula
        a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        
        # Distance in meters
        return R * c

    def get_bounding_box(self, lat, lon, distance):
        # Earth's radius in meters
        R = 6371000  
        
        # Convert distance from meters to degrees (approximate)
        lat_delta = distance / R * (180 / 3.14159)
        lon_delta = distance / (R * cos(radians(lat))) * (180 / 3.14159)
        
        # Calculate the bounding box
        min_lat = lat - lat_delta
        max_lat = lat + lat_delta
        min_lon = lon - lon_delta
        max_lon = lon + lon_delta
    
        return (min_lat, max_lat, min_lon, max_lon)

    def filter_stops_in_bounding_box(self, stops, lat, lon, distance):
        # Get bounding box coordinates
        min_lat, max_lat, min_lon, max_lon = self.get_bounding_box(lat, lon, distance)
        
        # Filter stops within the bounding box
        return [stop for stop in stops if min_lat <= stop.stop_y <= max_lat and min_lon <= stop.stop_x <= max_lon]

    def get_walkable_stops(self, stops, curr_stop, max_distance, avg_walking_speed):
        # Filter stops inside the bounding box first
        candidate_stops = self.filter_stops_in_bounding_box(stops, curr_stop.stop_y, curr_stop.stop_x, max_distance)
        
        # Filter based on the exact distance using Haversine formula
        for stop in candidate_stops:
            distance = self.haversine(curr_stop.stop_y, curr_stop.stop_x, stop.stop_y, stop.stop_x)
            # make sure person can walk to the stop in time (assuming the latest we leave is when the bus at the stop we're currently at arrives) 
            time_delta = distance / avg_walking_speed
            time_delta = timedelta(seconds=time_delta)
            if distance <= max_distance and curr_stop.arrival_time + time_delta <= stop.arrival_time:
                curr_stop.children.append(NodeCostPair(stop, distance))
                curr_stop.children_ids.add(stop.id)

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
            # if curr_node.id not in builded_walk:
            #     self._build_walk(curr_node)
            #     builded_walk.add(curr_node.id)

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
        # print(f'building walk cost {time()-time0}')

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
                # cost shouldn't be 0 since it's a different stop
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

        # walk 
        # add node that are reacheable through walking to its children
        for node in self.nodes:
            self.get_walkable_stops(self.nodes, node, self.max_walking_distance, self.avg_walking_speed)

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
