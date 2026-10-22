from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select, update
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Customer


class CustomerRepository:

    @staticmethod
    async def get_by_mobile(mobile_number: str, session: AsyncSession) -> Optional[Customer]:
        result = await session.execute(select(Customer).where(Customer.mobile_number == mobile_number))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_or_create_locked(
        mobile_number: str, full_name: str, email: Optional[str], session: AsyncSession
    ) -> Customer:
        await session.execute(
            pg_insert(Customer)
            .values(mobile_number=mobile_number, full_name=full_name, email=email,
                    loyalty_points=0, registered_at=datetime.now(timezone.utc))
            .on_conflict_do_nothing(index_elements=[Customer.mobile_number])
        )
        result = await session.execute(
            select(Customer)
            .where(Customer.mobile_number == mobile_number)
            .with_for_update()
            .execution_options(populate_existing=True)
        )
        return result.scalar_one()

    @staticmethod
    async def add_points(customer_id: int, points: int, session: AsyncSession) -> int:
        result = await session.execute(
            update(Customer)
            .where(Customer.customer_id == customer_id)
            .values(loyalty_points=Customer.loyalty_points + points)
            .returning(Customer.loyalty_points)
        )
        return result.scalar_one()
