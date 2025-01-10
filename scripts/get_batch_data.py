from datetime import datetime, timedelta
from helper.weather_api import get_historical_weather

## Paramters
data_path = "Data/"
X_features = ["temp_c",
              "is_day",
              "wind_kph",
              "wind_degree", #(wind_cos() et wind_sin())
              "wind_dir",  # (à encoder ou voir si wind_degree)
              "pressure_mb",
              "humidity",
              "humidity",
              "cloud",
              "feelslike_c",
              "windchill_c",
              "heatindex_c",
              "dewpoint_c",
              "vis_km",
              "gust_kph",
              "uv",
              "lat",
              "lon"
]
Y_target = "precip_mm"

## Time limits of the collection
current_date = datetime.now()
one_week_before = current_date - timedelta(days=7)    # 7 is the maximum number of days for which we can retrieve past data

train_start_date = one_week_before.strftime("%Y-%m-%d")
train_end_date = current_date.strftime("%Y-%m-%d")

## Get the data
def get_data(cities, X_features, Y_target, start_date, end_date):

    return data