from decimal import Decimal
from typing import Annotated, Generic, TypeVar

from pydantic import BaseModel, ConfigDict, PlainSerializer
from pydantic.alias_generators import to_camel

T = TypeVar("T")

Money = Annotated[Decimal, PlainSerializer(lambda v: float(v), return_type=float, when_used="json")]


class CamelModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True, from_attributes=True)


class ApiResponse(BaseModel, Generic[T]):
    success: bool = True
    message: str = "OK"
    data: T
from datetime import datetime
from typing import Annotated

from pydantic import StringConstraints, field_validator

from app.core.utils import normalize_mobile, validate_email
from app.schemas.common import CamelModel


class CustomerInput(CamelModel):
    full_name: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=150)]
    mobile_number: str
    email: str | None = None

    @field_validator("mobile_number")
    @classmethod
    def _mobile(cls, v: str) -> str:
        return normalize_mobile(v)

    @field_validator("email")
    @classmethod
    def _email(cls, v: str | None) -> str | None:
        if v is None or not v.strip():
            return None
        return validate_email(v)


class CustomerResponse(CamelModel):
    customer_id: int
    mobile_number: str
    full_name: str
    email: str | None
    registered_at: datetime
    loyalty_points: int
