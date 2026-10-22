from decimal import Decimal
from typing import Annotated

from pydantic import Field, StrictInt, StringConstraints

from app.schemas.common import CamelModel, Money

NonEmpty = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]


class ProductCreate(CamelModel):
    product_name: NonEmpty = Field(max_length=150)
    unique_product_code: NonEmpty = Field(max_length=50)
    unit_price: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    available_quantity: StrictInt = Field(ge=0)
    active_status: bool = True
    category_id: StrictInt


class ProductResponse(CamelModel):
    product_id: int
    unique_product_code: str
    product_name: str
    unit_price: Money
    available_quantity: int
    active_status: bool
    category_id: int
    category_name: str
