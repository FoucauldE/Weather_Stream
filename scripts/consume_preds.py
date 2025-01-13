from helper.kafka_utils import create_kafka_consumer, consume_messages_from_kafka
import time

INPUT_TOPIC = 'rain-prediction-output'
consumer_predictions = create_kafka_consumer(INPUT_TOPIC, group_id='output-preds-group')

if __name__ == "__main__":

    while True:
        for prediction in consume_messages_from_kafka(consumer_predictions):
            print(prediction)
        time.sleep(60)