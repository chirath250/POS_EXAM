from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.schemas import ApiResponse, OrderCreate, OrderResponse
from app.services.order_service import OrderService

router = APIRouter(prefix="/api/v1/orders", tags=["Orders"])


@router.post("", response_model=ApiResponse[OrderResponse], status_code=status.HTTP_201_CREATED)
async def place_order(order_data: OrderCreate, session: AsyncSession = Depends(get_session)):
    order = await OrderService.place_order(order_data, session)
    return ApiResponse(message="Order completed", data=order)
