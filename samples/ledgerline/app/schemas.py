from pydantic import BaseModel


class OrderIn(BaseModel):
    customer_id: int
    sku: str
    quantity: int


class OrderOut(OrderIn):
    id: int
    status: str
