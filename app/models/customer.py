from datetime import datetime, timezone

from sqlalchemy import CheckConstraint, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


def _now() -> datetime:
    return datetime.now(timezone.utc)


class Customer(Base):
    __tablename__ = "loyalty_customers"
    __table_args__ = (CheckConstraint("loyalty_points >= 0", name="ck_customers_points"),)

    customer_id: Mapped[int] = mapped_column(primary_key=True)
    mobile_number: Mapped[str] = mapped_column(String(13), unique=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(150), nullable=False)
    email: Mapped[str | None] = mapped_column(String(150))
    loyalty_points: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    registered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=_now)
