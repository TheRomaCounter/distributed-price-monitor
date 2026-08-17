import asyncio
from celery import Celery
from celery.schedules import crontab
import httpx
from sqlalchemy.future import select
from app.config import settings
from app.database import async_session, Product, PriceHistory

celery_app = Celery(
    "tasks",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL
)

celery_app.conf.beat_schedule = {
    "check-prices-every-30-seconds": {
        "task": "app.worker.check_all_products_loop",
        "schedule": 30.0,
    },
}
celery_app.conf.timezone = "UTC"

async def update_product_price_in_db(url: str):
    new_price = 1499.0
    async with async_session() as session:
        async with session.begin():
            result = await session.execute(select(Product).filter(Product.url == url))
            product = result.scalars().first()
            if product:
                product.current_price = new_price
                history_entry = PriceHistory(product_id=product.id, price=new_price)
                session.add(history_entry)

@celery_app.task(name="app.worker.check_all_products_loop")
def check_all_products_loop():
    loop = asyncio.get_event_loop()
    async def get_and_check():
        async with async_session() as session:
            result = await session.execute(select(Product))
            products = result.scalars().all()
            for p in products:
                await update_product_price_in_db(p.url)
    loop.run_until_complete(get_and_check())
    return {"status": "batch_success"}

@celery_app.task(name="app.worker.check_product_price")
def check_product_price(url: str):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(update_product_price_in_db(url))
    return {"status": "success", "url": url}
