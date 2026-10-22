from decimal import Decimal

from sqlalchemy import CheckConstraint, ForeignKey, Integer, Numeric, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class OrderItem(Base):
    __tablename__ = "order_items"
    __table_args__ = (
        CheckConstraint("quantity > 0", name="ck_items_qty_positive"),
        UniqueConstraint("order_id", "product_id", name="uq_items_order_product"))

    order_item_id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("customer_orders.order_id"), nullable=False, index=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.product_id"), nullable=False, index=True)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)   # snapshot
    subtotal: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)     # snapshot

    order = relationship("Order", back_populates="items")
    product = relationship("Product", lazy="raise")
