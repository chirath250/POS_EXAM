from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.schemas import ApiResponse, CustomerResponse
from app.services.loyalty_service import LoyaltyService

router = APIRouter(prefix="/api/v1/loyalty-customers", tags=["Loyalty"])


@router.get("", response_model=ApiResponse[CustomerResponse])
async def find_loyalty_customer(
    mobile_number: str = Query(..., alias="mobileNumber"),
    session: AsyncSession = Depends(get_session),
):
    customer = await LoyaltyService.find_customer(mobile_number, session)
    return ApiResponse(data=customer)
