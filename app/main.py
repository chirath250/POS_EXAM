from fastapi import FastAPI

from app.core.exceptions import register_exception_handlers
from app.routers import loyalty_customers, orders, products, sales

app = FastAPI(title="POS Orders & Customer Loyalty API", version="1.0.0")
register_exception_handlers(app)
for r in (products.router, orders.router, loyalty_customers.router, sales.router):
    app.include_router(r)
