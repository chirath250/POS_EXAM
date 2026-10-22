from decimal import Decimal
from typing import Optional, List

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import noload

from app.models import Category, Product
from app.schemas import ProductCreate, ProductResponse


class CategoryRepository:

    @staticmethod
    async def get_category_by_id(category_id: int, session: AsyncSession) -> Optional[Category]:
        return await session.get(Category, category_id)


class ProductRepository:

    @staticmethod
    async def create_product(
        product_data: ProductCreate,
        session: AsyncSession
    ) -> ProductResponse:

        new_product = Product(
            product_name=product_data.product_name,
            unique_product_code=product_data.unique_product_code,
            unit_price=product_data.unit_price,
            available_quantity=product_data.available_quantity,
            active=product_data.active_status,
            category_id=product_data.category_id,
        )

        session.add(new_product)
        await session.commit()
        await session.refresh(new_product, ["category"])

        return ProductResponse.model_validate(new_product)

    @staticmethod
    async def get_by_code(code: str, session: AsyncSession) -> Optional[Product]:
        result = await session.execute(select(Product).where(Product.unique_product_code == code))
        return result.scalar_one_or_none()

    @staticmethod
    async def search_products(
        name: Optional[str],
        min_price: Optional[Decimal],
        max_price: Optional[Decimal],
        category_id: Optional[int],
        session: AsyncSession
    ) -> List[ProductResponse]:

        stmt = select(Product)
        if name:
            escaped = name.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
            stmt = stmt.where(Product.product_name.ilike(f"%{escaped}%", escape="\\"))
        if min_price is not None:
            stmt = stmt.where(Product.unit_price >= min_price)
        if max_price is not None:
            stmt = stmt.where(Product.unit_price <= max_price)
        if category_id is not None:
            stmt = stmt.where(Product.category_id == category_id)

        result = await session.execute(stmt.order_by(Product.product_id))
        return [ProductResponse.model_validate(p) for p in result.scalars().all()]

    @staticmethod
    async def get_products_for_update(ids: List[int], session: AsyncSession) -> List[Product]:
        stmt = (
            select(Product)
            .where(Product.product_id.in_(ids))
            .order_by(Product.product_id)
            .options(noload(Product.category))
            .with_for_update(of=Product))
        result = await session.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def decrement_stock(product_id: int, quantity: int, session: AsyncSession) -> bool:
        result = await session.execute(
            update(Product)
            .where
            (Product.product_id == product_id, Product.available_quantity >= quantity)
            .values
            (available_quantity=Product.available_quantity - quantity))
        return result.rowcount == 1




