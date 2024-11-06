from sqlalchemy.orm import Session
from database import Order
from schemas import OrderCreate
from confluent_kafka import Consumer
from config import KAFKA_BROKER_URL, KAFKA_TOPIC, KAFKA_GROUP_ID
import json
from database import SessionLocal
from crud import archive_order
import datetime

from logger import logger


def archive_order(db: Session, order_data: dict):
    # Check if the order already exists
    existing_order = db.query(Order).filter(Order.id == order_data["order_id"]).first()
    if existing_order:
        # Update the existing order
        existing_order.item_name = order_data["item_name"]
        existing_order.quantity = order_data["quantity"]
        existing_order.price = order_data["price"]
        db.commit()
        logger.info(f"Updated order {order_data['order_id']}")
    else:
        # Insert a new order
        new_order = Order(
            id=order_data["order_id"],
            item_name=order_data["item_name"],
            quantity=order_data["quantity"],
            price=order_data["price"]
        )
        db.add(new_order)
        db.commit()
        logger.info(f"Inserted new order {order_data['order_id']}")


class KafkaConsumer:
    def __init__(self, broker_url=KAFKA_BROKER_URL, topic=KAFKA_TOPIC, group_id=KAFKA_GROUP_ID):
        self.consumer = Consumer({
            "bootstrap.servers": broker_url,
            "group.id": group_id,
            "auto.offset.reset": "earliest",
        })
        self.consumer.subscribe([topic])

    def consume_and_store(self):
        db = SessionLocal()
        try:
            while True:
                msg = self.consumer.poll(1.0)
                if msg is None:
                    continue
                if msg.error():
                    logger.info(f"Consumer error: {msg.error()}")
                    continue

                order_data = json.loads(msg.value().decode("utf-8"))
                order_data["processed_timestamp"] = str(datetime.datetime.now())
                archive_order(db, order_data)
                logger.info(f"Processed order: {order_data}")
        finally:
            db.close()
            self.consumer.close()


if __name__ == '__main__':
    # Instantiate a KafkaConsumer object
    kafka_consumer = KafkaConsumer()
    kafka_consumer.consume_and_store()
