from datetime import datetime
from config.config import VARIABLES_TO_KEEP, TARGET_VARIABLE
import math

def convert_timestamp(timestamp_ms, include_time=False):
    # From unix timestamp (in ms) to human readable

    timestamp_sec = timestamp_ms / 1000
    dt = datetime.utcfromtimestamp(timestamp_sec)

    if include_time:
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    else:
        return dt.strftime('%Y-%m-%d')
    

def preprocess_data(data):
    """
    Filters and encodes the input data to retain only the desired variables,
    transforms 'wind_degree' into its sine and cosine components and extracts the target variable.
    Also returns the last update epoch (used to identify if new data arrived)
    """
    
    nested_data = data.get('data', {})

    filtered_data = {}
    for key in VARIABLES_TO_KEEP:
        if key in nested_data:
            filtered_data[key] = nested_data[key]
    
    if 'wind_degree' in filtered_data:
        wind_degree = nested_data['wind_degree']
        radians = math.radians(wind_degree)
        filtered_data['wind_degree_sin'] = math.sin(radians)
        filtered_data['wind_degree_cos'] = math.cos(radians)

    target = nested_data.get(TARGET_VARIABLE, None)
    last_updated = nested_data.get('last_updated_epoch', None)

    return last_updated, filtered_data, target