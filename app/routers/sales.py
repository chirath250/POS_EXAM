from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.schemas import ApiResponse, SalesSummaryResponse
from app.services.sales_service import SalesService

router = APIRouter(prefix="/api/v1/sales", tags=["Sales"])


@router.get("/summary", response_model=ApiResponse[SalesSummaryResponse])
async def get_daily_summary(
    business_date: date = Query(..., alias="date"),
    session: AsyncSession = Depends(get_session),
):
    summary = await SalesService.get_daily_summary(business_date, session)
    return ApiResponse(data=summary)
