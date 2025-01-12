from helper.kafka_utils import create_kafka_producer, create_kafka_consumer, send_message_to_kafka, consume_messages_from_kafka
import pandas as pd
from config.config import TARGET_VARIABLE, CITIES_LIST
import time
from river import compose, linear_model, metrics, preprocessing
from kafka import KafkaConsumer
import json


def main():
    # Kafka configuration
    KAFKA_TOPIC_TRAIN = "weather_train"
    KAFKA_TOPIC_TEST = "weather_test"
    KAFKA_BOOTSTRAP_SERVER = "localhost:9092"

    # Variables
    MAX_MESSAGES_TRAIN = int(len(CITIES_LIST) * 24 * 8 * 0.8)
    MAX_MESSAGES_TEST = int(len(CITIES_LIST) * 24 * 8 * 0.2)

    # Loading the data
    train_data = pd.read_csv("Data/train_data_historical.csv")
    test_data = pd.read_csv("Data/test_data_historical.csv")

    # Kafka Producer
    producer = create_kafka_producer()

    print("Sending train data to Kafka...")
    for index, row in train_data.iterrows():
        producer.send(KAFKA_TOPIC_TRAIN, value=row.to_dict())
        time.sleep(0.1)

    print("Sending test data to Kafka...")
    for index, row in test_data.iterrows():
        producer.send(KAFKA_TOPIC_TEST, value=row.to_dict())
        time.sleep(0.1)

    # River for online learning
    model = compose.Pipeline(
        preprocessing.StandardScaler(),
        linear_model.LinearRegression()
    )
    metric = metrics.R2()

    # Kafka Consumer
    #consumer_train = create_kafka_consumer(KAFKA_TOPIC_TRAIN, auto_offset_reset='earliest')
    consumer_train = KafkaConsumer(KAFKA_TOPIC_TRAIN, bootstrap_servers=KAFKA_BOOTSTRAP_SERVER, auto_offset_reset='earliest', value_deserializer=lambda x: json.loads(x.decode('utf-8')))
    consumer_test = KafkaConsumer(KAFKA_TOPIC_TEST, bootstrap_servers=KAFKA_BOOTSTRAP_SERVER, auto_offset_reset='earliest', value_deserializer=lambda x: json.loads(x.decode('utf-8')))
    #consumer_test = create_kafka_consumer(KAFKA_TOPIC_TEST, auto_offset_reset='earliest')

    # Train
    last_precip = None
    i = 0
    print("Training...")
    for message in consumer_train:
        if i >= MAX_MESSAGES_TRAIN:  # Stop after the max number of iterations is reached
            break
        data_point = message.value

        # Prepare features and target
        features = {key: value for key, value in data_point.items() if key != TARGET_VARIABLE}
        current_precip = data_point[TARGET_VARIABLE]

        if last_precip is not None and features is not None:
            # Train the model
            model.learn_one(features, last_precip)
            print(i)

        # Update the loop variables
        last_precip = current_precip
        i += 1

    # Test
    last_precip = None
    print("Test...")
    i = 0

    for message in consumer_test:
        if i >= MAX_MESSAGES_TEST:  # Stop after the max number of iterations is reached
            break
        data_point = message.value

        print(i)

        # Prepare features and target
        features = {key: value for key, value in data_point.items() if key != TARGET_VARIABLE}
        current_precip = data_point[TARGET_VARIABLE]

        if last_precip is not None:
            # Predict the next value of 'precip_mm'
            prediction = model.predict_one(features)
            print("YES",i)
            # Evaluate the performance
            metric.update(current_precip, prediction)
            print(f"Actual value: {current_precip:.2f}, Prediction: {prediction:.2f}, R²: {metric.get():.4f}")

        # Update the loop variables
        last_precip = current_precip
        i += 1
        
    print("End of the testing part.")
    print(f"Final R²: {metric.get():.4f}")

    return(metric.get())