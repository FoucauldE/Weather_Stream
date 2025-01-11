from kafka import KafkaProducer, KafkaConsumer
import json
from config.config import KAFKA_BROKER

def create_kafka_producer():
    producer = KafkaProducer(
        bootstrap_servers=KAFKA_BROKER,
        value_serializer=lambda v: json.dumps(v).encode('utf-8'),
    )
    return producer

def send_message_to_kafka(producer, output_topic, message):
    producer.send(output_topic, message)
    producer.flush()

def create_kafka_consumer(input_topic):
    consumer = KafkaConsumer(
        input_topic,
        bootstrap_servers=KAFKA_BROKER,
        group_id='weather_group',
        value_deserializer=lambda m: json.loads(m.decode('utf-8')),
    )
    return consumer

def consume_messages_from_kafka(consumer):
    for message in consumer:
        yield message.value
