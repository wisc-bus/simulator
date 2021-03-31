import os
from ..util import tomin


class SearchResult():
    BITMASK = [0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80]
    DAY = ["monday", "tuesday", "wednesday",
           "thursday", "friday", "saturday", "sunday"]

    def __init__(self, busSim, grid_size_min):
        self.data = b""
        self.no_removal_data = b""
        self.day = self.DAY.index(busSim.day)
        self.start_time = tomin(busSim.start_time)
        self.elapse_time = tomin(busSim.elapse_time)
        # self.start_points = config["start_points"]
        self.avg_walking_speed = busSim.avg_walking_speed
        self.max_walking_min = busSim.max_walking_min
        self.grid_size_min = grid_size_min
        self.x_num, self.y_num, _ = busSim._get_grid_dimention(grid_size_min)
        self.data_block_size = (self.x_num * self.y_num + 7) // 8

    def get_out_filename(self):
        return f"search-result-{self.day}-{self.start_time}"

    def record(self, start_point, grid, route_remove=None):
        data = self._serialize_grid(grid)
        if route_remove == None:
            self.no_removal_data += data
        self.data += data

    def record_batch(self, route_remove):
        self.data += self.no_removal_data

    def to_bytes(self):
        header = self._serialize_header()
        return header + self.data

    def _serialize_grid(self, grid):
        data = bytearray(self.data_block_size)
        for y, row in enumerate(grid):
            for x, bit in enumerate(row):
                if bit == 1:
                    pos = y * self.x_num + x
                    data[pos // 8] |= self.BITMASK[pos % 8]
        return data

    def _serialize_header(self):
        return self.day.to_bytes(1, byteorder='big') + \
            self.start_time.to_bytes(2, byteorder='big') + \
            self.elapse_time.to_bytes(1, byteorder='big') + \
            self.max_walking_min.to_bytes(1, byteorder='big') + \
            self.grid_size_min.to_bytes(1, byteorder='big') + \
            self.x_num.to_bytes(2, byteorder='big') + \
            self.y_num.to_bytes(2, byteorder='big')
