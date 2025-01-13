from helper.kafka_utils import create_kafka_producer, send_message_to_kafka
from helper.weather_api import get_current_weather, get_forecast_weather, get_historical_weather
import time

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


if __name__ == "__main__":
    # to test without streamlit (with default loc: Paris)
    print("Starting collecting live data...")
    start_ingesting_live_data('Paris')