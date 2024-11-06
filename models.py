from sqlalchemy import Column, Integer, String, Float
from db import Base


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    item_name = Column(String, index=True)
    quantity = Column(Integer)
    price = Column(Float)

class OrderEvent(Base):
    __tablename__ = 'order_events'
    id = Column(Integer, primary_key=True, index=True)
    item = Column(String, index=True)
    quantity = Column(Integer)
    price = Column(Float)