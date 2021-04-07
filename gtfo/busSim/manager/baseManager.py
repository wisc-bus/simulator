class BaseManager():
    def __init__(self, gtfs_path, borders):
        self.gtfs_path = gtfs_path
        self.borders = borders

    def get_borders(self):
        return self.borders

    def run_batch(self, busSim_params, start_time, start_points, route_remove):
        pass

    def read_gtfs(self, filename):
        pass

    def save(self, result):
        pass
