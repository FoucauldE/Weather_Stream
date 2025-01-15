import threading
import streamlit as st
import pandas as pd
from datetime import datetime
from scripts.ingest_data import get_past_data
from scripts.online_model import train_and_predict
from helper.kafka_utils import create_kafka_consumer, create_kafka_producer

st.title("🔮 Predictions")

location = st.text_input("Enter City Name or Zip Code", "Biarritz")
start_button = st.button("Start Data Collection and Predictions")

data = pd.DataFrame()
graph_container = st.empty()
metrics_container = st.empty()

def display_predictions(topic, group_id):
    status_message.empty()
    consumer = create_kafka_consumer(topic, group_id)

    try:
        for message in consumer:
            new_data = pd.DataFrame([message.value])
            new_data['timestamp'] = new_data['timestamp'].apply(lambda ts: datetime.fromtimestamp(ts))

            if not new_data.empty:
                global data
                data = pd.concat([data, new_data]).drop_duplicates().sort_index()

                with metrics_container.container():
                    latest_row = data.iloc[-1]
                    st.metric("Prediction (mm)", round(latest_row['prediction'], 2))
                    st.metric("Actual (mm)", round(latest_row['actual'], 2))

                with graph_container.container():
                    st.line_chart(data[['timestamp', 'prediction', 'actual']].set_index('timestamp'))

    except Exception as e:
        st.error(f"Error consuming data: {e}")
        consumer.close()

if start_button:
    status_message = st.empty()
    status_message.info("Starting past and live data collection...")

    producer_data = create_kafka_producer()

    collection_thread = threading.Thread(target=get_past_data, args=(location,), daemon=True)
    collection_thread.start()

    predictions_thread = threading.Thread(target=train_and_predict, daemon=True)
    predictions_thread.start()

    display_predictions('rain-prediction-output', 'prediction-group')
