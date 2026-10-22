from datetime import datetime
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Order, OrderItem


class SalesRepository:

    @staticmethod
    async def get_summary(
        start: datetime, end: datetime, session: AsyncSession
    ) -> tuple[int, int, Decimal, int]:

        window = (
            Order.order_status == "COMPLETED",
            Order.order_date_time >= start,
            Order.order_date_time < end,
        )
        orders_row = (await session.execute(
            select(
                func.count(Order.order_id),
                func.coalesce(func.sum(Order.total_amount), 0),
                func.coalesce(func.sum(Order.loyalty_points_earned), 0),
            ).where(*window)
        )).one()
        units = (await session.execute(
            select(func.coalesce(func.sum(OrderItem.quantity), 0))
            .join(Order, Order.order_id == OrderItem.order_id)
            .where(*window)
        )).scalar_one()

        return int(orders_row[0]), int(units), Decimal(orders_row[1]), int(orders_row[2])
