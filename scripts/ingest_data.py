import time
import csv
import os
import pytz
import pandas as pd
from datetime import datetime, timedelta
from helper.kafka_utils import create_kafka_producer, send_message_to_kafka
from helper.weather_api import get_current_weather, get_forecast_weather, get_historical_weather, get_timezone_id
from helper.tools import preprocess_data
from config.config import CITIES_LIST, DATA_DIR, MAX_HISTORY_DAYS

OUTPUT_TOPIC = 'weather-data'

default_producer = create_kafka_producer()

def fetch_and_send_current_weather(location, output_topic, producer=default_producer, to_preprocess=False):
    current_weather = get_current_weather(location)
    if current_weather:
        message = {'type': 'current', 'data': current_weather}
        if to_preprocess:
            message = preprocess_data(message)[0]
        send_message_to_kafka(producer, output_topic, message)
        return current_weather
    return None


def fetch_and_send_forecast_weather(location, forecast_days):
    forecast_weather = get_forecast_weather(location, days=forecast_days)
    if forecast_weather:
        send_message_to_kafka(default_producer, OUTPUT_TOPIC, {'type': 'forecast', 'data': forecast_weather})
        return forecast_weather
    return None


def fetch_and_send_historical_weather(location, date, hour=None):
    historical_weather = get_historical_weather(location, date=date, hour=hour)
    if historical_weather:
        send_message_to_kafka(default_producer, OUTPUT_TOPIC, {'type': 'historical', 'data': historical_weather})
        return historical_weather
    return None

def start_ingesting_live_data(location):
    """Used for predictions on live data"""
    while True:
        fetch_and_send_current_weather(location, 'weather-live-data-2', to_preprocess=True)
        time.sleep(60)

def define_collection_timespan(location=None):
    """Define the timespan for data collection, adjusted to the timezone of the specified location."""

    if location is None:
        location = CITIES_LIST[0]
    local_timezone = pytz.timezone(get_timezone_id(location))
    
    current_date = datetime.now(local_timezone)
    beginning_date = current_date - timedelta(days=MAX_HISTORY_DAYS)
    
    return beginning_date, current_date


def get_past_data(location=None, output_csv_name=None):
    """
    Collect weather data for the past week and either save it to a CSV to train a batch model,
    or send it through a producer to train an online model.
    """

    headers = None
    live_producer = None
    start_date, end_date = define_collection_timespan(location)
    date = start_date
    stop_before = end_date.hour

    if output_csv_name:
        os.makedirs(DATA_DIR, exist_ok=True)
        output_csv_path = os.path.join(DATA_DIR, output_csv_name)
        csvfile = open(output_csv_path, mode="w", newline="", encoding="utf-8")
        writer = None
    else:
        live_producer = create_kafka_producer()
        
    while date <= end_date:
        for city in (CITIES_LIST if location is None else [location]):
            raw_data = get_historical_weather(location=city, date=date)
            processed_data = preprocess_data(raw_data)

            for hour, hourly_data in enumerate(processed_data):

                # if it's the last day, stop before current hour
                if date.date() == end_date.date() and hour >= stop_before:
                    break

                row = {
                    "last_updated": hourly_data["last_updated"],
                    "target": hourly_data["target"]
                }

                if output_csv_name:
                    row.update(hourly_data["processed_sample"])
                    if headers is None:
                        headers = list(row.keys())
                        writer = csv.DictWriter(csvfile, fieldnames=headers)
                        writer.writeheader()
                    writer.writerow(row)

                else:
                    row["processed_sample"] = hourly_data["processed_sample"]
                    send_message_to_kafka(live_producer, 'weather-live-data-2', row)

        date += timedelta(days=1)

    if output_csv_name:
        csvfile.close()

    else:
        start_ingesting_live_data(location)

def format_csv(csv_name="all_weather_data.csv", prediction_distance=1, delete_first_csv=False):
    """
    Input: csv file
    Output: the same but with the target added at the end of each line
    """
    # Load the csv file
    csv_path = "Data/" + csv_name
    df = pd.read_csv(csv_path)

    # Add the last column of the next row to the current row
    df['futur_target'] = df['target'].shift(-prediction_distance)
    df = df.iloc[:-1]
    
    # Drop columns for which the following lat,lon are not the same
    df["next_lat"] = df['lat'].shift(-1)
    df["next_lon"] = df['lon'].shift(-1)

    # Keep only the rows with the same lat, lon
    df_filtered = df[(df['lat'] == df["next_lat"]) & (df['lon'] == df["next_lon"])]

    # Delete the temporary columns
    df_filtered = df_filtered.drop(columns=["next_lat", "next_lon"])
    
    # Save to a new CSV file
    base_directory = os.path.dirname(csv_path)
    output_file_path = os.path.join(base_directory, csv_name[:-4] + "_with_Y.csv")
    df_filtered.to_csv(output_file_path, index=False)
    if delete_first_csv:
        base_directory = os.path.dirname(csv_path)
        first_file_path = os.path.join(base_directory, csv_name)
        os.remove(first_file_path)

def ingest_hist_data_streamlit(file_name):
    get_past_data(location=None, output_csv_name=file_name)
    format_csv(csv_name=file_name, delete_first_csv=True)

def default_file_name():
    train_start_date, train_end_date = define_collection_timespan()
    # Convert date for file name
    formatted_date_start = train_start_date.strftime("%Y-%m-%d")
    formatted_date_end = train_end_date.strftime("%Y-%m-%d")    
    file_name = f"{formatted_date_start}_{formatted_date_end}_past_data.csv"

    return file_name


if __name__ == "__main__":
    train_start_date, train_end_date = define_collection_timespan()
    # Convert date for file name
    formatted_date_start = train_start_date.strftime("%Y-%m-%d")
    formatted_date_end = train_end_date.strftime("%Y-%m-%d")    
    file_name = f"{formatted_date_start}_{formatted_date_end}_past_data.csv"
    get_past_data(location=None, output_csv_name=file_name)
    format_csv(csv_name=file_name)