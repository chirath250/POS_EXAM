from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Order


class OrderRepository:

    @staticmethod
    async def add_order(order: Order, session: AsyncSession) -> Order:
        session.add(order)
        await session.flush()
        return order
