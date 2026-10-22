from decimal import Decimal
from typing import Optional, List

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import BusinessRuleError, ConflictError, NotFoundError, ValidationAppError
from app.repositories.product_repository import CategoryRepository, ProductRepository
from app.schemas import ProductCreate, ProductResponse


class ProductService:

    @staticmethod
    async def create_product(product_data: ProductCreate, session: AsyncSession) -> ProductResponse:
        category = await CategoryRepository.get_category_by_id(product_data.category_id, session)
        if category is None:
            raise NotFoundError(f"Category {product_data.category_id} not found")
        if not category.active:
            raise BusinessRuleError(f"Category {product_data.category_id} is inactive")
        if await ProductRepository.get_by_code(product_data.unique_product_code, session):
            raise ConflictError(f"Product code '{product_data.unique_product_code}' already exists")

        try:
            return await ProductRepository.create_product(product_data, session)
        except IntegrityError:  # concurrent duplicate: the unique constraint is the final guard
            await session.rollback()
            raise ConflictError(f"Product code '{product_data.unique_product_code}' already exists")

    @staticmethod
    async def search_products(
        name: Optional[str],
        min_price: Optional[Decimal],
        max_price: Optional[Decimal],
        category_id: Optional[int],
        session: AsyncSession
    ) -> List[ProductResponse]:
        name = (name or "").strip() or None
        if min_price is not None and max_price is not None and min_price > max_price:
            raise ValidationAppError("minPrice must not be greater than maxPrice")
        return await ProductRepository.search_products(name, min_price, max_price, category_id, session)
