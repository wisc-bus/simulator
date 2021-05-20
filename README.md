# SCanalyzer

## Installation

### Production
```
pip install SCanalyzer
```

### Development
```
git clone https://github.com/wisc-bus/simulator.git
cd simulator
virtualenv venv && source venv/bin/activate
pip install -r requirements.txt
```

## Usage

### Overview
To run BusSim:
```python
from SCanalyzer import SCanalyzer
from SCanalyzer.busSim import Config

sc = SCanalyzer(PATH_TO_GTFS_ZIP)
config = Config(day="monday", elapse_time="00:30:00", interval="01:00:00", max_walking_min=10) # run sim on Monday's schedule; run over a 30 min window for every hour; limit max walking to 10 min
config.set_starts(points=[(43.073691, -89.387407)]) # set the starting point
result_gdf = sc.search(config) # run Sim
```

To run a full analysis with census and services
```python
sc = SCanalyzer(PATH_TO_GTFS_ZIP)
config = Config(day="monday", elapse_time="00:30:00", interval="01:00:00", max_walking_min=10) # run sim on Monday's schedule; run over a 30 min window for every hour; limit max walking to 10 min
census_gdf = sc.load_census() # load the census data of the region
config.set_starts(centroids=census_gdf) # set the starting points to be the centers of each census tracks
result_gdf = sc.search(config) # run Sim
services_gdf = sc.load_yelp(api_key=YOUR_YELP_API_KEY) # load service data from yelp
sc.add_service_metrics(result_gdf, services_gdf) # combine Sim result with service data
sc.add_demographic_metrics(result_gdf, census_gdf) # combine Sim result with census data
result_gdf
```

See more usage in ```notebooks/example.ipynb```



### Census Class:

* See Census class example notebook for some of the features of the class. 
