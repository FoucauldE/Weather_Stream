import time
import csv
import os
import pandas as pd
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
                # print(hourly_data)
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
                    send_message_to_kafka(producer, 'data-previous-week', row)

        date += timedelta(days=1)

    if output_csv_name:
        csvfile.close()

def format_csv(csv_name="all_weather_data.csv", prediction_distance=1):
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



if __name__ == "__main__":
    # to test without streamlit (with default loc: Paris)
    # print("Starting collecting live data...")
    # start_ingesting_live_data('Paris')
    print("Starting collecting past week data")
    train_start_date, train_end_date = define_collection_timespan()
    # Convert date for file name
    formatted_date_start = train_start_date.strftime("%Y-%m-%d_%H-%M-%S")
    formatted_date_end = train_end_date.strftime("%Y-%m-%d_%H-%M-%S")    
    file_name = f"{formatted_date_start}_{formatted_date_end}_past_data.csv"
    get_past_data(location=None, output_csv_name=file_name)
    format_csv(csv_name=file_name)