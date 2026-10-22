from decimal import Decimal
from typing import Optional, List

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.schemas import ApiResponse, ProductCreate, ProductResponse
from app.services.product_service import ProductService

router = APIRouter(prefix="/api/v1/products", tags=["Products"])


@router.post("", response_model=ApiResponse[ProductResponse], status_code=status.HTTP_201_CREATED)
async def create_product(product_data: ProductCreate, session: AsyncSession = Depends(get_session)):
    product = await ProductService.create_product(product_data, session)
    return ApiResponse(message="Product created", data=product)


@router.get("", response_model=ApiResponse[List[ProductResponse]])
async def search_products(
    name: Optional[str] = Query(None),
    min_price: Optional[Decimal] = Query(None, alias="minPrice", ge=0),
    max_price: Optional[Decimal] = Query(None, alias="maxPrice", ge=0),
    category_id: Optional[int] = Query(None, alias="categoryId", gt=0),
    session: AsyncSession = Depends(get_session),
):
    products = await ProductService.search_products(name, min_price, max_price, category_id, session)
    return ApiResponse(data=products)
