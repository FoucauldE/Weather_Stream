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

    filtered_data = {}
    for key in VARIABLES_TO_KEEP:
        if key in data:
            filtered_data[key] = data[key]
    
    if 'wind_degree' in filtered_data:
        wind_degree = filtered_data.pop('wind_degree')  # Remove original key
        radians = math.radians(wind_degree)
        filtered_data['wind_degree_sin'] = math.sin(radians)
        filtered_data['wind_degree_cos'] = math.cos(radians)

    if TARGET_VARIABLE in data:
        target = data[TARGET_VARIABLE]

    last_updated = data['last_updated_epoch']

    return last_updated, filtered_data, target

def preprocess_historical_data(data):
    "This function "
    processed_data = {}
    
    # Extract latitude, longitude and city name
    lat = data.get("lat", None)
    lon = data.get("lon", None)

    # Initialize dictionary for processed data
    processed_data["hours"] = []

    # Iterate over forecast days
    for day in data.get("forecastday", []):
        for hour in day.get("hour", []):
            # Extract relevant fields
            time_epoch = hour.get("time_epoch")
            temp_c = hour.get("temp_c")
            is_day = hour.get("is_day")
            wind_kph = hour.get("wind_kph")
            wind_degree = hour.get("wind_degree")
            pressure_mb = hour.get("pressure_mb")
            humidity = hour.get("humidity")
            cloud = hour.get("cloud")
            feelslike_c = hour.get("feelslike_c")
            windchill_c = hour.get("windchill_c")
            heatindex_c = hour.get("heatindex_c")
            dewpoint_c = hour.get("dewpoint_c")
            vis_km = hour.get("vis_km")
            gust_kph = hour.get("gust_kph")
            uv = hour.get("uv")
            precip_mm = hour.get("precip_mm")

            # Convert wind degree to sine and cosine
            wind_degree_rad = math.radians(wind_degree) if wind_degree is not None else None
            wind_sin = math.sin(wind_degree_rad) if wind_degree_rad is not None else None
            wind_cos = math.cos(wind_degree_rad) if wind_degree_rad is not None else None

            # Append processed data for this hour
            processed_data["hours"].append({
                "lat": lat,
                "lon": lon,
                "time_epoch": time_epoch,
                "temp_c": temp_c,
                "is_day": is_day,
                "wind_kph": wind_kph,
                "wind_sin": wind_sin,
                "wind_cos": wind_cos,
                "pressure_mb": pressure_mb,
                "humidity": humidity,
                "cloud": cloud,
                "feelslike_c": feelslike_c,
                "windchill_c": windchill_c,
                "heatindex_c": heatindex_c,
                "dewpoint_c": dewpoint_c,
                "vis_km": vis_km,
                "gust_kph": gust_kph,
                "uv": uv,
                "precip_mm": precip_mm
            })

    return processed_data