from decimal import Decimal

from sqlalchemy import Boolean, CheckConstraint, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.category import Category


class Product(Base):
    __tablename__ = "products"
    __table_args__ = (CheckConstraint("unit_price > 0", name="ck_products_price_positive"),
        CheckConstraint("available_quantity >= 0", name="ck_products_stock_nonneg"),)

    product_id: Mapped[int] = mapped_column(primary_key=True)
    unique_product_code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    product_name: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    available_quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.category_id"), nullable=False, index=True)

    category: Mapped[Category] = relationship(lazy="joined", innerjoin=True)

    @property
    def active_status(self) -> bool:
        return self.active

    @property
    def category_name(self) -> str:
        return self.category.category_name
