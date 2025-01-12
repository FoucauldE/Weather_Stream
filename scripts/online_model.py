from sklearn.linear_model import SGDRegressor
from river.metrics import MSE
from river.compat.sklearn_to_river import convert_sklearn_to_river
from helper.kafka_utils import create_kafka_consumer, consume_messages_from_kafka, create_kafka_producer, send_message_to_kafka
from helper.tools import preprocess_data
import json
import time
from config.config import KAFKA_BROKER

from scripts.ingest_data import fetch_and_send_current_weather


INPUT_TOPIC = 'weather-live-data'
OUTPUT_TOPIC = 'rain-prediction-output'
CONSUMER_GROUP = 'rain-prediction-group'

consumer = create_kafka_consumer(INPUT_TOPIC)
producer = create_kafka_producer()

sklearn_model = SGDRegressor() # change to load pre-trained model
model = convert_sklearn_to_river(sklearn_model)
metric = MSE()


def train_and_predict():
    """
    Consume messages from Kafka, train the model incrementally, and make predictions.
    """

    previous_timestamp, previous_features = None, None
    # margin_seconds = 180 # +/- 3 mins margin

    for message in consume_messages_from_kafka(consumer):
        # print(f"Received message: {message}")
        
        timestamp, features, target = preprocess_data(message)
        # print(timestamp)
        # print(features)
        
        if previous_features is not None:
            # print('is not 1st')
            time_diff = timestamp - previous_timestamp
            print(time_diff)
            # check if data from an hour later (might need to allow a margin, ie not exactly 3600s)
            # if timestamp - previous_timestamp == 3600:
            # if timestamp - previous_timestamp == 15*60:
            # if 15*60 - margin_seconds <= time_diff <= 15*60 + margin_seconds:
            if timestamp - previous_timestamp == 15*60:
                # print('is new')
                print("Evaluate model and update...")
                y_pred = model.predict_one(previous_features)
                metric.update(target, y_pred)
                model.learn_one(previous_features, target)

                send_message_to_kafka(producer, OUTPUT_TOPIC, {
                    'timestamp': timestamp,
                    'prediction': y_pred,
                    'actual': target
                })
                print(f"Prediction: {y_pred}, Actual: {target}")
                
        previous_timestamp, previous_features = timestamp, features

        time.sleep(60)


if __name__ == "__main__":
    print("Starting online learning model...")
    # consumer_preds = create_kafka_consumer('rain-prediction-output')

    while True:

        train_and_predict()

        """
        for message in consume_messages_from_kafka(consumer_preds):
            prediction = message.value
            print(f"Prediction for next 15min: {prediction['prediction']} mm")
            print(f"Actual value: {prediction['actual']} mm")
        """

        time.sleep(60)
