from datetime import date, datetime, time, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.utils import COLOMBO
from app.repositories.sales_repository import SalesRepository
from app.schemas import SalesSummaryResponse


class SalesService:

    @staticmethod
    async def get_daily_summary(day: date, session: AsyncSession) -> SalesSummaryResponse:
        start = datetime.combine(day, time.min, tzinfo=COLOMBO)
        end = datetime.combine(day + timedelta(days=1), time.min, tzinfo=COLOMBO)
        count, units, revenue, points = await SalesRepository.get_summary(start, end, session)
        return SalesSummaryResponse(
            date=day, completed_order_count=count, total_units_sold=units,
            total_sales_revenue=revenue, total_loyalty_points_earned=points)
