from sklearn.linear_model import SGDRegressor
from river.metrics import MSE
from river.compat.sklearn_to_river import convert_sklearn_to_river
from helper.kafka_utils import create_kafka_consumer, consume_messages_from_kafka, create_kafka_producer, send_message_to_kafka
import json
import time
from config.config import KAFKA_BROKER
from river import linear_model, metrics, preprocessing


# INPUT_TOPIC = 'weather-live-data'
input_topic_past_data = 'data-previous-week'
OUTPUT_TOPIC = 'rain-prediction-output'
CONSUMER_GROUP = 'rain-prediction-group'

# consumer = create_kafka_consumer(INPUT_TOPIC, 'live-weather-consumer-group')
producer_predictions = create_kafka_producer()

sklearn_model = SGDRegressor()
model = convert_sklearn_to_river(sklearn_model)
metric = MSE()

scaler = preprocessing.StandardScaler()



def train_and_predict(consumer):
    """
    Consume messages from Kafka, train the model incrementally, and send predictions.
    """

    previous_timestamp, previous_features, previous_target = None, None, None

    for message in consume_messages_from_kafka(consumer):
        
        timestamp, features, target = message["last_updated"], message["processed_sample"], message["target"]
        
        if previous_features is not None:
            # check if data from an hour later (might need to allow a margin, ie not exactly 3600s)
            if timestamp - previous_timestamp == 3600:
                # features["prev_target"] = previous_target
                scaler.learn_one(previous_features)
                scaled_prev_features = scaler.transform_one(previous_features)

                y_pred = model.predict_one(scaled_prev_features)
                metric.update(target, y_pred)
                model.learn_one(scaled_prev_features, target)

                send_message_to_kafka(producer_predictions, OUTPUT_TOPIC, {
                    'timestamp': timestamp,
                    'prediction': y_pred,
                    'actual': target
                })
                print(f"Prediction: {y_pred}, Actual: {target}")
                
        previous_timestamp, previous_features, previous_target = timestamp, features, target


if __name__ == "__main__":
    print("Starting online learning model...")
    # consumer_preds = create_kafka_consumer('rain-prediction-output')

    consumer_past_data = create_kafka_consumer(input_topic_past_data, 'past-data-group')
    while True:
        train_and_predict(consumer_past_data)

        """
        for message in consume_messages_from_kafka(consumer_preds):
            prediction = message.value
            print(f"Prediction for next 15min: {prediction['prediction']} mm")
            print(f"Actual value: {prediction['actual']} mm")
        """

        # time.sleep(10)
