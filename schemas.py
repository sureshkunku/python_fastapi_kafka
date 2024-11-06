from pydantic import BaseModel


class OrderCreate(BaseModel):
    item_name: str
    quantity: int
    price: float


class OrderResponse(OrderCreate):
    id: int

    class Config:
        orm_mode = True
