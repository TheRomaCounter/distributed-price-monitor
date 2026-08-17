from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import Product, PriceHistory
from app.schemas import ProductCreate

async def get_product_by_url(db: AsyncSession, url: str):
    result = await db.execute(select(Product).filter(Product.url == url))
    return result.scalars().first()

async def create_product(db: AsyncSession, product_in: ProductCreate):
    db_product = Product(
        title="Заглушка (парсинг позже)",
        url=str(product_in.url),
        current_price=0.0
    )
    db.add(db_product)
    await db.commit()
    await db.refresh(db_product)
    
    db_history = PriceHistory(
        product_id=db_product.id,
        price=0.0
    )
    db.add(db_history)
    await db.commit()
    
    return db_product
