from datetime import datetime, timedelta
from helper.weather_api import get_historical_weather
from config.config import VARIABLES_TO_KEEP, TARGET_VARIABLE

## Paramters
data_path = "Data/"

## Time limits of the collection
current_date = datetime.now()
one_week_before = current_date - timedelta(days=7)    # 7 is the maximum number of days for which we can retrieve past data

train_start_date = one_week_before.strftime("%Y-%m-%d")
train_end_date = current_date.strftime("%Y-%m-%d")

## Get the data
def get_data(cities, X_features, Y_target, start_date, end_date):

    return data