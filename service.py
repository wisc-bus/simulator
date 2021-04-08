import requests
import pandas as pd
import geopandas as gpd

def get_info(data, key='name'):
    final = []
    for item in data:
        obj = item[key]
        final.append(obj)
    return final


def get_results(keyword, api_key, lat=None, lon=None, location=None, radius=40000): # keyword, api_key are a must. Either both lat and lon, or a location (such as 'Madison, Wisconsin') must be provided. Radius is good to specify, but need to integrate with Megan's census information
    endpoint = 'https://api.yelp.com/v3/businesses/search'
    headers = {'Authorization': 'bearer %s' % api_key}
    assert lat != None and lon != None or location != None
    if location != None:
        parameters = {
        'term': keyword,
        'limit':50,
        'radius':radius,
        'location':'Madison, Wisconsin'}
    else:
        parameters = {
        'term': keyword,
        'limit':50,
        'radius':radius,
        'latitude':lat,
        'longitude':lon}
    all_results = []
    response = requests.get(url=endpoint, params=parameters, headers=headers)
    result = response.json()
    all_results += result['businesses']
    
    found = result['total']
    searches = found // 50 
    
    if searches != 0:
        for i in range(searches):
            offset = (i+1) * 50
            parameters['offset'] = offset
            response = requests.get(url=endpoint, params=parameters, headers=headers)
            result = response.json()
            all_results += result['businesses']
    
 
    df = pd.DataFrame()
    for col in keys:
        df[col] = get_info(all_results, key=col)
    return df