import time
import csv
import os
from datetime import datetime, timedelta
from helper.kafka_utils import create_kafka_producer, send_message_to_kafka
from helper.weather_api import get_current_weather, get_forecast_weather, get_historical_weather
from helper.tools import preprocess_data
from config.config import CITIES_LIST, DATA_DIR, MAX_HISTORY_DAYS

OUTPUT_TOPIC = 'weather-data'

producer = create_kafka_producer()

def fetch_and_send_current_weather(location, output_topic):
    current_weather = get_current_weather(location)
    if current_weather:
        send_message_to_kafka(producer, output_topic, {'type': 'current', 'data': current_weather})
        return current_weather
    return None


def fetch_and_send_forecast_weather(location, forecast_days):
    forecast_weather = get_forecast_weather(location, days=forecast_days)
    if forecast_weather:
        send_message_to_kafka(producer, OUTPUT_TOPIC, {'type': 'forecast', 'data': forecast_weather})
        return forecast_weather
    return None


def fetch_and_send_historical_weather(location, date, hour=None):
    historical_weather = get_historical_weather(location, date=date, hour=hour)
    if historical_weather:
        send_message_to_kafka(producer, OUTPUT_TOPIC, {'type': 'historical', 'data': historical_weather})
        return historical_weather
    return None

def start_ingesting_live_data(location):
    """Used for predictions on live data"""
    while True:
        fetch_and_send_current_weather(location, 'weather-live-data')
        time.sleep(60)

def define_collection_timespan():

    current_date = datetime.now()
    beginning_date = current_date - timedelta(days=MAX_HISTORY_DAYS)
    train_start_date = beginning_date.strftime("%Y-%m-%d")
    train_end_date = current_date.strftime("%Y-%m-%d")
    train_start_date = datetime.strptime(train_start_date, "%Y-%m-%d")
    train_end_date = datetime.strptime(train_end_date, "%Y-%m-%d")

    return train_start_date, train_end_date


def get_past_data(location=None, output_csv_name=None):
    """
    Collect weather data for the past week and either save it to a CSV to train a batch model,
    or send it through a producer to train an online model.
    """

    headers = None
    producer = None
    start_date, end_date = define_collection_timespan()
    date = start_date

    if output_csv_name:
        os.makedirs(DATA_DIR, exist_ok=True)
        output_csv_path = os.path.join(DATA_DIR, output_csv_name)
        csvfile = open(output_csv_path, mode="w", newline="", encoding="utf-8")
        writer = None
    else:
        producer = create_kafka_producer()
        
    while date <= end_date:
        for city in (CITIES_LIST if location is None else [location]):
            raw_data = get_historical_weather(location=city, date=date)
            processed_data = preprocess_data(raw_data)

            for hourly_data in processed_data:
                print(hourly_data)
                row = {
                    "last_updated": hourly_data["last_updated"],
                    "processed_sample": hourly_data["processed_sample"],
                    "target": hourly_data["target"] # ,
                    # **hourly_data["processed_sample"]
                }

                if output_csv_name:
                    if headers is None:
                        headers = list(row.keys())
                        writer = csv.DictWriter(csvfile, fieldnames=headers)
                        writer.writeheader()
                    writer.writerows(row)

                else:
                    send_message_to_kafka(producer, 'data-previous-week', row)
                time.sleep(10)

        date += timedelta(days=1)

    if output_csv_name:
        csvfile.close()


if __name__ == "__main__":
    # to test without streamlit (with default loc: Paris)
    # print("Starting collecting live data...")
    # start_ingesting_live_data('Paris')
    print("Starting collecting past week data")
    get_data('Paris')
