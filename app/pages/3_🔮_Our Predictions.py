import streamlit as st
import time
from scripts.ingest_data import fetch_and_send_current_weather, start_ingesting_live_data
from helper.kafka_utils import create_kafka_consumer, consume_messages_from_kafka
from scripts.online_model import train_and_predict
import threading

def start_background_task():
    thread = threading.Thread(target=train_and_predict)
    thread.start()

INPUT_TOPIC = 'rain-prediction-output'
consumer_predictions = create_kafka_consumer(INPUT_TOPIC)

st.set_page_config(page_title="Predictions", page_icon="🔮")
st.title('🔮 Predictions')

location = st.text_input("Enter City Name or Zip Code", "Brest")
prediction_placeholder = st.empty()
last_data = None

if st.button("Start Live Predictions"):
    start_background_task()
    if not location:
        st.error("Please enter a valid location.")
    else:
        with prediction_placeholder.container():
            try:
                start_ingesting_live_data(location)

                while True:
                    train_and_predict()

                    for prediction in consume_messages_from_kafka(consumer_predictions):
                        print(prediction)
                        st.write(f"Prediction for next hour: {prediction['prediction']} mm")
                        st.write(f"Actual value: {prediction['actual']} mm")

                    time.sleep(60)

            except Exception as e:
                st.error(f"An error occurred: {e}")