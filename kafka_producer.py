from confluent_kafka import Producer
import json
from config import KAFKA_BROKER_URL, KAFKA_TOPIC
from logger import logger

class KafkaProducer:
    def __init__(self, broker_url=KAFKA_BROKER_URL, topic=KAFKA_TOPIC):
        self.producer = Producer({"bootstrap.servers": broker_url})
        self.topic = topic

    def publish(self, message: dict, key: str = None):
        self.producer.produce(
            self.topic,
            key=key,
            value=json.dumps(message)
        )
        self.producer.flush()
        logger.info(f"Published message to topic '{self.topic}': {message}")


if __name__ == '__main__':
    kafka_producer = KafkaProducer()
    kafka_producer.publish({"order_id": 123, "status": "confirmed"})