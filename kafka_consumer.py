from confluent_kafka import Consumer, KafkaException
import json
from config import KAFKA_BOOTSTRAP_SERVERS, KAFKA_TOPIC, KAFKA_GROUP_ID
from db import SessionLocal
from models import Order, OrderEvent
from logger import logger


def archive_order(db, order_data):
    action = order_data.get("action")

    if action == "create":
        existing_order = db.query(OrderEvent).filter(OrderEvent.id == order_data["id"]).first()
        if existing_order:
            logger.warning(f"Order {order_data['id']} already exists. Skipping creation.")
        else:
            new_order = OrderEvent(
                id=order_data["id"],
                item=order_data["item"],
                quantity=order_data["quantity"],
                price=order_data["price"]
            )
            db.add(new_order)
            db.commit()
            logger.info(f"Inserted new order {order_data['id']}")

    elif action == "update":
        existing_order = db.query(OrderEvent).filter(OrderEvent.id == order_data["id"]).first()
        if existing_order:
            existing_order.item = order_data['order']["item"]
            existing_order.quantity = order_data['order']["quantity"]
            existing_order.price = order_data['order']["price"]
            db.add(existing_order)
            db.commit()
            logger.info(f"Updated OrderEvent {order_data['id']}")
        else:
            logger.warning(f"OrderEvent {order_data['id']} not found for update.")

    elif action == "delete":
        existing_order = db.query(OrderEvent).filter(OrderEvent.id == order_data["id"]).first()
        if existing_order:
            db.delete(existing_order)
            db.commit()
            logger.info(f"Deleted OrderEvent {order_data['id']}")
        else:
            logger.warning(f"OrderEvent {order_data['id']} not found for deletion.")
    else:
        logger.error(f"Unknown action: {action}")


class KafkaConsumer:
    def __init__(self, broker_url=KAFKA_BOOTSTRAP_SERVERS, topic=KAFKA_TOPIC, group_id=KAFKA_GROUP_ID):
        self.consumer = Consumer({
            "bootstrap.servers": broker_url,
            "group.id": group_id,
            "auto.offset.reset": "earliest"
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
                    logger.error(f"Consumer error: {msg.error()}")
                    continue

                order_data = json.loads(json.loads(msg.value().decode("utf-8")))
                archive_order(db, order_data)
                logger.info(f"Processed order: {order_data}")
        finally:
            db.close()
            self.consumer.close()


if __name__ == '__main__':
    kafka_consumer = KafkaConsumer()
    kafka_consumer.consume_and_store()
