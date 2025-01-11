from sklearn.linear_model import LinearRegression
from river.metrics import MeanSquaredError
from river.utils import convert_sklearn_to_river
from helper.kafka_utils import create_kafka_consumer, consume_messages_from_kafka, create_kafka_producer, send_message_to_kafka
from helper.tools import preprocess_data
import json
import time
from config.config import KAFKA_BROKER

INPUT_TOPIC = 'weather-data'
OUTPUT_TOPIC = 'rain-prediction-output'
CONSUMER_GROUP = 'rain-prediction-group'

consumer = create_kafka_consumer(INPUT_TOPIC)
producer = create_kafka_producer()

sklearn_model = LinearRegression() # change to load pre-trained model
model = convert_sklearn_to_river(sklearn_model)
metric = MeanSquaredError()


def train_and_predict():
    """
    Consume messages from Kafka, train the model incrementally, and make predictions.
    """

    previous_timestamp, previous_features = None, None

    for message in consume_messages_from_kafka(consumer):
        print(f"Received message: {message}")
        
        timestamp, features, target = preprocess_data(message)
        
        if previous_features is not None:
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

        time.sleep(3)


if __name__ == "__main__":
    print("Starting online learning model...")
    train_and_predict()
