from datetime import datetime
from config.config import VARIABLES_TO_KEEP, TARGET_VARIABLE
import math
 

def preprocess_data(data):
    """
    Filters and encodes the input data to retain only the desired variables,
    transforms 'wind_degree' into its sine and cosine components and extracts the target variable.
    Also returns the last update epoch (used to identify if new data arrived)
    """

    def preprocess_single_sample(data_sample, lat, lon, epoch_var_name):
        """
        Preprocesses a single data sample by filtering, encoding, and extracting target variables.
        """

        processed_sample = {}
        for key in VARIABLES_TO_KEEP:
            if key in data_sample:
                processed_sample[key] = data_sample[key]

        wind_degree = data_sample['wind_degree']
        radians = math.radians(wind_degree)
        processed_sample['wind_degree_sin'] = math.sin(radians)
        processed_sample['wind_degree_cos'] = math.cos(radians)

        processed_sample['lat'], processed_sample['lon'] = lat, lon

        target = data_sample.get(TARGET_VARIABLE, None)
        last_updated = data_sample.get(epoch_var_name, None)

        return last_updated, processed_sample, target

    is_live_data = 'type' in data and data['type'] == 'current'
    
    if is_live_data:
        processed_samples = []
        nested_data = data.get('data', {})
        lat, lon = nested_data.get("lat", None), nested_data.get("lon", None)
        last_updated, processed_sample, target = preprocess_single_sample(nested_data, lat, lon, 'last_updated_epoch')
        processed_samples.append({
            "last_updated": last_updated,
            "processed_sample": processed_sample,
            "target": target
        })
    else:
        processed_samples = []
        lat, lon = data.get("lat", None), data.get("lon", None)
        day_data = data.get("forecastday", [])[0]
        hourly_data = day_data.get('hour', [])
        for hour_data in hourly_data:
            last_updated, processed_sample, target = preprocess_single_sample(hour_data, lat, lon, 'time_epoch')
            
            processed_samples.append({
                "last_updated": last_updated,
                "processed_sample": processed_sample,
                "target": target
            })

    return processed_samples