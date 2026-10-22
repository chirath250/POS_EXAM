from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import BusinessRuleError, ConflictError, NotFoundError
from app.models import Order, OrderItem
from app.repositories.customer_repository import CustomerRepository
from app.repositories.order_repository import OrderRepository
from app.repositories.product_repository import ProductRepository
from app.schemas import OrderCreate, OrderCustomerResponse, OrderItemResponse, OrderResponse
from app.services.loyalty_service import LoyaltyService

CENT = Decimal("0.01")


class OrderService:

    @staticmethod
    async def place_order(order_data: OrderCreate, session: AsyncSession) -> OrderResponse:
        try:
            # 1. Lock requested products (ascending id) and validate each line.
            locked = {
                p.product_id: p
                for p in await ProductRepository.get_products_for_update(
                    sorted(i.product_id for i in order_data.items), session)
            }
            lines, total = [], Decimal("0.00")
            for item in order_data.items:
                product = locked.get(item.product_id)
                if product is None:
                    raise NotFoundError(f"Product {item.product_id} not found")
                if not product.active:
                    raise BusinessRuleError(f"Product {product.unique_product_code} is inactive")
                if product.available_quantity < item.quantity:
                    raise ConflictError(
                        f"Insufficient stock for {product.unique_product_code}: requested "
                        f"{item.quantity}, available {product.available_quantity}")
                subtotal = (product.unit_price * item.quantity).quantize(CENT)
                lines.append((product, item.quantity, product.unit_price, subtotal))
                total += subtotal

            points = LoyaltyService.calculate_points(total)

            # 2. Reduce stock atomically.
            for product, qty, _, _ in lines:
                if not await ProductRepository.decrement_stock(product.product_id, qty, session):
                    raise ConflictError(f"Insufficient stock for {product.unique_product_code}")

            # 3. Resolve / enrol customer (race-safe), credit points atomically.
            c = order_data.customer
            customer = await CustomerRepository.get_or_create_locked(
                c.mobile_number, c.full_name, c.email, session)
            balance = await CustomerRepository.add_points(customer.customer_id, points, session)

            # 4. Persist order with price / subtotal snapshots.
            order = Order(
                customer_id=customer.customer_id,
                order_date_time=datetime.now(timezone.utc),
                order_status="COMPLETED",
                total_amount=total,
                loyalty_points_earned=points,
                items=[OrderItem(product_id=p.product_id, quantity=q, unit_price=up, subtotal=st)
                       for p, q, up, st in lines],
            )
            await OrderRepository.add_order(order, session)

            response = OrderResponse(
                order_id=order.order_id,
                order_date_time=order.order_date_time,
                order_status=order.order_status,
                customer=OrderCustomerResponse(
                    customer_id=customer.customer_id, mobile_number=customer.mobile_number,
                    full_name=customer.full_name, email=customer.email),
                items=[OrderItemResponse(
                    product_id=p.product_id, unique_product_code=p.unique_product_code,
                    product_name=p.product_name, quantity=q, unit_price=up, subtotal=st)
                    for p, q, up, st in lines],
                total_amount=total,
                loyalty_points_earned=points,
                loyalty_balance=balance,
            )
            await session.commit()
            return response

        except IntegrityError:
            await session.rollback()
            raise ConflictError("Order could not be saved because of a data integrity conflict")
        except Exception:
            await session.rollback()
            raise
