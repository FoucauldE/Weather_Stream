from datetime import datetime, timedelta
import pandas as pd
from sklearn.model_selection import train_test_split
from helper.weather_api import get_historical_weather
from helper.tools import preprocess_historical_data
from config.config import VARIABLES_TO_KEEP, TARGET_VARIABLE, CITIES_LIST
import csv
import os

def define_settings(data_path="Data/", output_csv="all_weather_data.csv"):
    """
    Define settings with which we will download the data.
    """
    # Paramters
    data_path = "Data/"
    os.makedirs(data_path, exist_ok=True)
    output_csv = "all_weather_data.csv"
    output_csv_path = os.path.join(data_path, output_csv)

    # Time limits of the collection
    current_date = datetime.now()
    one_week_before = current_date - timedelta(days=7)  # 7 is the maximum number of days for which we can retrieve past data

    train_start_date = one_week_before.strftime("%Y-%m-%d")
    train_end_date = current_date.strftime("%Y-%m-%d")

    train_start_date = datetime.strptime(train_start_date, "%Y-%m-%d")
    train_end_date = datetime.strptime(train_end_date, "%Y-%m-%d")

    return train_start_date, train_end_date, output_csv_path

def get_data(start_date, end_date, output_csv_path):
    """
    Provide the historical data of the 8 previous days in a csv format.
    """
    headers = VARIABLES_TO_KEEP + [TARGET_VARIABLE]
    print("headers put")
    with open(output_csv_path, mode="w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=headers)
        writer.writeheader()

        date = start_date
        while date <= end_date:
            for city in CITIES_LIST:
                data = get_historical_weather(location=city, date=date, hour=None)
                processed_data = preprocess_historical_data(data)
                for hour_data in processed_data.get("hours", []):
                    writer.writerow(hour_data)

            date += timedelta(days=1)
    print("Data collected")

def train_test_csv(file_path):
    # Get the file
    file_path = file_path
    data = pd.read_csv(file_path)
    base_directory = os.path.dirname(file_path)
    # Split into train and test
    train_data, test_data = train_test_split(data, test_size=0.2, random_state=42)
    # Output file paths
    train_file_path = os.path.join(base_directory, 'train_data_historical.csv')
    test_file_path = os.path.join(base_directory, 'test_data_historical.csv')
    # # Save the outputs
    train_data.to_csv(train_file_path, index=False)
    test_data.to_csv(test_file_path, index=False)