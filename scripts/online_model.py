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

consumer = create_kafka_consumer(INPUT_TOPIC, 'live-weather-consumer-group')
producer = create_kafka_producer()

sklearn_model = SGDRegressor() # change to load pre-trained model
model = convert_sklearn_to_river(sklearn_model)
metric = MSE()


def train_and_predict(consumer):
    """
    Consume messages from Kafka, train the model incrementally, and make predictions.
    Currently adapted to receive live data.
    Should be modified to receive data from the preceding week in order to perform online learning on this data,
    before keeping predicting and adjusting on live data.
    """

    previous_timestamp, previous_features = None, None
    # margin_seconds = 180 # +/- 3 mins margin

    for message in consume_messages_from_kafka(consumer):

        preprocessed_data = preprocess_data(message)[0]
        timestamp, features, target = preprocessed_data.values()
        
        if previous_features is not None:
            time_diff = timestamp - previous_timestamp
            print(time_diff)
            # check if data from an hour later (might need to allow a margin, ie not exactly 3600s)
            if timestamp - previous_timestamp == 3600:
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
