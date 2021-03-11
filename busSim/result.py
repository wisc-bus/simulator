import os


class Result():
    BITMASK = [0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80]

    def __init__(self, config):
        self.data = []
        self.day = config["day"]
        self.start_time = config["start_time"]
        self.elapse_time = config["elapse_time"]
        self.start_points = config["start_points"]
        self.avg_walking_speed = config["avg_walking_speed"]
        self.max_walking_min = config["max_walking_min"]
        self.grid_size_min = config["grid_size_min"]
        self.x_num = config["x_num"]
        self.y_num = config["y_num"]
        self.data_block_size = (self.x_num * self.y_num + 7) // 8

    def record(self, start_point, grid):
        data = self._serialize_grid(grid)
        self.data.append(data)

    def save(self, filename):
        # header = self._serialize_header()
        with open(filename, "wb") as f:
            for data in self.data:
                f.write(data)

    def _serialize_grid(self, grid):
        data = bytearray(self.data_block_size)
        for y, row in enumerate(grid):
            for x, bit in enumerate(row):
                if bit == 1:
                    pos = y * self.x_num + x
                    data[pos // 8] |= self.BITMASK[pos % 8]
        return data

    def _serialize_header(self):
        pass
