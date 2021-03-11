class Result():

    def __init__(self, run_config):
        self.run_config = run_config

    def record(self, start_point, grid):
        print(f"{start_point} recorded")

    def __str__(self):
        return super().__str__()

    def to_packet(self):
        pass
