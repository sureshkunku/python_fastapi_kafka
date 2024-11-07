import uvicorn
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import json

import db, models, schemas
from kafka_producer import KafkaProducer
from logger import logger

app = FastAPI()
models.Base.metadata.create_all(bind=db.engine)
producer = KafkaProducer()


# Create Order
@app.post("/orders/", response_model=schemas.OrderResponse)
def create_order(order: schemas.OrderCreate, db: Session = Depends(db.get_db)):
    db_order = models.Order(**order.dict())
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    order_message = json.dumps({
        "action": "create",
        "id": db_order.id,
        "item": order.item,
        "quantity": order.quantity,
        "price": order.price})
    order_message = order_message
    producer.publish(order_message)
    return db_order


# Read Order
@app.get("/orders/{id}", response_model=schemas.OrderResponse)
def read_order(id: int, db: Session = Depends(db.get_db)):
    order = db.query(models.Order).filter(models.Order.id == id).first()
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


# Update Order
@app.put("/orders/{id}", response_model=schemas.OrderResponse)
def update_order(id: int, order: schemas.OrderCreate, db: Session = Depends(db.get_db)):
    db_order = db.query(models.Order).filter(models.Order.id == id).first()
    if db_order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    for key, value in order.dict().items():
        setattr(db_order, key, value)
    db.commit()
    db.refresh(db_order)
    order_message = json.dumps({"action": "update", "id": id, "order": order.dict()})
    producer.publish(order_message)
    return db_order


# Delete Order
@app.delete("/orders/{id}")
def delete_order(id: int, db: Session = Depends(db.get_db)):
    db_order = db.query(models.Order).filter(models.Order.id == id).first()
    if db_order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    db.delete(db_order)
    db.commit()
    order_message = json.dumps({"action": "delete", "id": id})
    producer.publish(order_message)
    return {"detail": "Order deleted successfully"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
