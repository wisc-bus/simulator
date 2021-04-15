from .manager import managerFactory
from ..util import tomin
from shapely.geometry import Point


class Config:
    def __init__(self, day, elapse_time, interval, avg_walking_speed=1.4, max_walking_min=None, grid_size_min=2, run_env="local"):
        self.params_ = {
            "run_env": run_env,
            "busSim_params": {
                "day": day,
                "elapse_time": elapse_time,
                "avg_walking_speed": avg_walking_speed,
                "max_walking_min": max_walking_min if max_walking_min != None else tomin(elapse_time),
                "grid_size_min": grid_size_min
            },
            "interval": interval,
            "start_points": []
        }

    def set_starts(self, points=[], centroids=None):
        if centroids is not None:
            self._set_starts_from_centroids(centroids)
        if len(points) > 0:
            self._set_starts_from_points(points)

    def get_start_points(self):
        return self.params_.get("start_points")

    def get_run_env(self):
        return self.params_.get("run_env")

    def get_interval(self):
        return self.params_.get("interval")

    def get_busSim_params(self):
        return self.params_.get("busSim_params")

    def is_runnable(self):
        # check run_env
        if self.params_.get("run_env") not in managerFactory.get_available_managers():
            return False

        # check start_points
        if len(self.params_.get("start_points")) == 0:
            return False

        return True

    def _set_starts_from_points(self, points):
        for point in points:
            if type(point) is tuple:
                self.params_["start_points"].append(point)
            elif type(point) is Point:
                self.params_["start_points"].append((point.y, point.x))

    def _set_starts_from_centroids(self, centroids):
        for poly in centroids["geometry"]:
            point = poly.centroid
            self.params_["start_points"].append((point.y, point.x))
