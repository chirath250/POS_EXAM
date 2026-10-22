from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError, ValidationAppError
from app.core.utils import normalize_mobile
from app.repositories.customer_repository import CustomerRepository
from app.schemas import CustomerResponse


class LoyaltyService:

    @staticmethod
    def calculate_points(total: Decimal) -> int:
        return int(total // Decimal("100"))

    @staticmethod
    async def find_customer(mobile_number: str, session: AsyncSession) -> CustomerResponse:
        try:
            mobile = normalize_mobile(mobile_number)
        except ValueError as e:
            raise ValidationAppError(str(e))

        customer = await CustomerRepository.get_by_mobile(mobile, session)
        if customer is None:
            raise NotFoundError(f"No loyalty customer found for {mobile}")
        return CustomerResponse.model_validate(customer)
