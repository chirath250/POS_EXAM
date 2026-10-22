from datetime import datetime

from pydantic import Field, StrictInt, field_validator

from app.schemas.common import CamelModel, Money
from app.schemas.customer import CustomerInput


class OrderItemRequest(CamelModel):
    product_id: StrictInt = Field(gt=0)
    quantity: StrictInt = Field(gt=0)


class OrderCreate(CamelModel):
    customer: CustomerInput
    items: list[OrderItemRequest] = Field(min_length=1)

    @field_validator("items")
    @classmethod
    def _no_duplicates(cls, items):
        ids = [i.product_id for i in items]
        if len(ids) != len(set(ids)):
            raise ValueError("Duplicate productId in items")
        return items


class OrderItemResponse(CamelModel):
    product_id: int
    unique_product_code: str
    product_name: str
    quantity: int
    unit_price: Money
    subtotal: Money


class OrderCustomerResponse(CamelModel):
    customer_id: int
    mobile_number: str
    full_name: str
    email: str | None


class OrderResponse(CamelModel):
    order_id: int
    order_date_time: datetime
    order_status: str
    customer: OrderCustomerResponse
    items: list[OrderItemResponse]
    total_amount: Money
    loyalty_points_earned: int
    loyalty_balance: int
