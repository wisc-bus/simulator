# a small tool to measure the memory usage, source: https://medium.com/survata-engineering-blog/monitoring-memory-usage-of-a-running-python-program-49f027e3d1ba

from concurrent.futures import ThreadPoolExecutor
import resource
from time import sleep
import time
import sys
from busSim import BusSim
from busSim.util import transform, gen_locations
import tracemalloc


def my_analysis_function():
    DATA_PATH = "./data"
    OUTPUT_PATH = "/tmp/output"
    DAY = "monday"
    START_TIME = "12:00:00"
    ELAPSE_TIME = "00:30:00"
    AVG_WALKING_SPEED = 1.4  # 1.4 meters per second
    MAX_WALKING_MIN = 10
    GRID_TIME = 2
    START_POINT_NUM = 1000

    config = {
        "data_path": DATA_PATH,
        "output_path": OUTPUT_PATH,
        "day": DAY,
        "start_time": START_TIME,
        "elapse_time": ELAPSE_TIME,
        "start_points": gen_locations(DATA_PATH, START_POINT_NUM),
        "avg_walking_speed": AVG_WALKING_SPEED,
        "max_walking_min": MAX_WALKING_MIN,
        "grid_size_min": GRID_TIME
    }
    result = BusSim.run(config)


def trace():
    tracemalloc.start()
    my_analysis_function()
    current, peak = tracemalloc.get_traced_memory()
    print(
        f"Current memory usage is {current / 10**6}MB; Peak was {peak / 10**6}MB")
    tracemalloc.stop()


class MemoryMonitor:
    def __init__(self):
        self.keep_measuring = True

    def measure_usage(self):
        max_usage = 0
        while self.keep_measuring:
            max_usage = max(
                max_usage,
                resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
            )
            sleep(0.1)

        return max_usage


def pool():
    with ThreadPoolExecutor() as executor:
        monitor = MemoryMonitor()
        mem_thread = executor.submit(monitor.measure_usage)
        try:
            fn_thread = executor.submit(my_analysis_function)
            result = fn_thread.result()
        finally:
            monitor.keep_measuring = False
            max_usage = mem_thread.result()

        print(f"Peak memory usage: {max_usage}")


if __name__ == "__main__":
    trace()
