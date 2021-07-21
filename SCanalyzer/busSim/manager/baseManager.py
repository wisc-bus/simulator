class BaseManager():
    def __init__(self, gtfs_path, borders):
        self.gtfs_path = gtfs_path
        self.borders = borders

    def get_borders(self):
        return self.borders

    def run_batch(self, config, perf_df=None):
        """run batch job 

        Args:
            config (SCanalyzer.busSim.Config): the config object for running the busSim

            perf_df (pandas.DataFrame): the optional df that keeps track of performance in the pipeline

        Returns:
            pandas.DataFrame: the result_df contains
                1. geometry - the shapely Point for each trip's starting point
                2. start_time - each trip's starting time
                3. map_identifier - identifier to index into a result file
        """
        pass

    def read_gtfs(self, filename):
        pass

    def save(self, result):
        pass
