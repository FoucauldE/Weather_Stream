from scripts.ingest_data import fetch_and_send_current_weather
from helper.kafka_utils import create_kafka_consumer, consume_messages_from_kafka, create_kafka_producer, send_message_to_kafka
import time

if __name__ == "__main__":
    print("Starting collecting live data...")

    while True:
        # Fetch current weather data from API and send to Kafka
        current_data = fetch_and_send_current_weather('Paris', 'weather-live-data')
        time.sleep(60)