import threading
import streamlit as st
import pandas as pd
import pytz
from datetime import datetime
from scripts.ingest_data import get_past_data
from scripts.online_model import train_and_predict
from helper.kafka_utils import create_kafka_consumer, create_kafka_producer
from helper.weather_api import get_timezone_id

PREDICTIONS_TOPIC = 'prediction-output'
st.set_page_config(page_title="Predictions", page_icon="☔")
st.title("🔮 Predictions 🌧️")

location = st.text_input("Enter City Name or Zip Code", "Montreal")
start_button = st.button("Start Predicting")

graph_container = st.empty()
metrics_container = st.empty()

def display_predictions(timezone):

    consumer = create_kafka_consumer(PREDICTIONS_TOPIC, 'preds-group')
    data = pd.DataFrame()

    try:
        for message in consumer:
            new_data = pd.DataFrame([message.value])
            new_data['timestamp'] = new_data['timestamp'].apply(lambda ts: datetime.fromtimestamp(ts, tz=timezone))

            if not new_data.empty:
                data = pd.concat([data, new_data]).drop_duplicates().sort_index()

                with metrics_container.container():
                    latest_row = data.iloc[-1]

                    mse_cols = st.columns(3)
                    mse_cols[0].metric("MSE Pre trained", round(latest_row['MSE pre trained'], 2), border=True)
                    mse_cols[1].metric("MSE cold start", round(latest_row['MSE cold start'], 2), border=True)
                    mse_cols[2].metric("MSE sklearn", round(latest_row['MSE sklearn'], 2), border=True)

                    # Write the next prediction in bold, centered inside a grey div
                    st.markdown(
                        f"""
                        <div style="text-align: center; background-color: #f0f0f0; padding: 10px; border-radius: 5px; margin-top: 20px;">
                            <strong style="font-size: 18px;">☔ Next Prediction: {round(latest_row['next prediction'], 2)} mm</strong>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                with graph_container.container():
                    st.markdown(
                        """
                        <h5 style="text-align: center;">Predicted vs Actual Rainfall (mm)</h5>
                        """,
                        unsafe_allow_html=True
                    )
                    st.line_chart(
                        data[['timestamp', 'prediction pre trained', 'prediction cold start', 'prediction sklearn', 'actual']]
                        .set_index('timestamp'),
                        use_container_width=True
                        )

    except Exception as e:
        st.error(f"Error consuming data: {e}")
        consumer.close()

if start_button:

    producer_data = create_kafka_producer()

    collection_thread = threading.Thread(target=get_past_data, args=(location,), daemon=True)
    collection_thread.start()

    predictions_thread = threading.Thread(target=train_and_predict, daemon=True)
    predictions_thread.start()

    local_timezone = pytz.timezone(get_timezone_id(location))

    display_predictions(local_timezone)
