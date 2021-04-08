import os
from ..util import tomin


class SearchResult():
    BITMASK = [0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80]
    DAY = ["monday", "tuesday", "wednesday",
           "thursday", "friday", "saturday", "sunday"]

    def __init__(self, busSim, grid_size_min):
        self.data = b""
        self.day = self.DAY.index(busSim.day)
        self.start_time = tomin(busSim.start_time)
        self.elapse_time = tomin(busSim.elapse_time)
        # self.avg_walking_speed = busSim.avg_walking_speed
        self.max_walking_min = busSim.max_walking_min
        self.grid_size_min = grid_size_min
        self.x_num, self.y_num, _ = busSim._get_grid_dimention(grid_size_min)
        self.data_block_size = (self.x_num * self.y_num + 7) // 8

    @classmethod
    def load_grid(cls, filename, idx):
        with open(filename, "rb") as f:
            # day = f.read(1)
            # start_time = f.read(2)
            # elapse_time = f.read(1)
            # max_walking_min = f.read(1)
            f.read(5)  # skip previous header for now
            grid_size_min = int.from_bytes(f.read(1), "big")
            x_num = int.from_bytes(f.read(2), "big")
            y_num = int.from_bytes(f.read(2), "big")
            data_block_size = (x_num * y_num + 7) // 8
            f.seek(data_block_size*idx, 1)
            grid = []
            row = []
            data = f.read(data_block_size)

            for i in range(x_num * y_num):
                x = i % x_num
                if x == 0 and i != 0:
                    grid.append(row)
                    row = []

                row.append(data[i // 8] >> (i % 8) & 0x01)

            grid.append(row)

        # TODO: fix this hardcoded 1.4 avg walking speed
        return grid, grid_size_min*1.4*60

    def get_out_filename(self):
        return f"search-result-{self.day}-{self.start_time}"

    def record(self, start_point, grid):
        data = self._serialize_grid(grid)
        self.data += data

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
