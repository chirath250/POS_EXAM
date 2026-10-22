from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Order(Base):
    __tablename__ = "customer_orders"  # ORDER is a reserved word
    __table_args__ = (
        CheckConstraint("total_amount >= 0", name="ck_orders_total_nonneg"),
        CheckConstraint("loyalty_points_earned >= 0", name="ck_orders_points_nonneg"),
        Index("ix_customer_orders_dt", "order_date_time"))

    order_id: Mapped[int] = mapped_column(primary_key=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("loyalty_customers.customer_id"), nullable=False, index=True)
    order_date_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    order_status: Mapped[str] = mapped_column(String(20), nullable=False, default="COMPLETED")
    total_amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    loyalty_points_earned: Mapped[int] = mapped_column(Integer, nullable=False)
    customer = relationship("Customer", lazy="raise")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan", lazy="selectin")
