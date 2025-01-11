import streamlit as st
import time
from scripts.ingest_data import (
    fetch_and_send_current_weather
)
from helper.kafka_utils import create_kafka_consumer, consume_messages_from_kafka

INPUT_TOPIC = 'rain-prediction-output'
consumer = create_kafka_consumer(INPUT_TOPIC)

st.set_page_config(page_title="Predictions", page_icon="🔮")
st.title('🔮 Predictions')

location = st.text_input("Enter City Name or Zip Code", "Brest")
prediction_placeholder = st.empty()
last_data = None

if st.button("Start Live Predictions"):
    if not location:
        st.error("Please enter a valid location.")
    else:
        st.success(f"Fetching weather data for {location} every ? seconds...")

        with prediction_placeholder.container():
            try:
                while True:
                    # Fetch current weather data from API and send to Kafka
                    current_data = fetch_and_send_current_weather(location)
                    # st.json(current_data)

                    for message in consume_messages_from_kafka(consumer):
                        prediction = message.value
                        st.write(f"Prediction for next hour: {prediction['prediction']} mm")
                        st.write(f"Actual value: {prediction['actual']} mm")

                    time.sleep(5)

            except Exception as e:
                st.error(f"An error occurred: {e}")