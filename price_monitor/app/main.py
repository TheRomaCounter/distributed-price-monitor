from contextlib import asynccontextmanager
from typing import List
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app import database, schemas, crud, worker

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with database.engine.begin() as conn:
        await conn.run_sync(database.Base.metadata.create_all)
    yield

app = FastAPI(title="Price Monitor API", version="1.0.0", lifespan=lifespan)

@app.post("/products", response_model=schemas.ProductResponse, status_code=status.HTTP_201_CREATED)
async def add_product(product_in: schemas.ProductCreate, db: AsyncSession = Depends(database.get_db)):
    db_product = await crud.get_product_by_url(db, url=str(product_in.url))
    if db_product:
        raise HTTPException(
            status_code=400,
            detail="Product with this URL already exists"
        )
    
    new_product = await crud.create_product(db, product_in)
    
    # Отправляем задачу на парсинг в Celery (выполняется в фоне)
    worker.check_product_price.delay(str(new_product.url))
    
    return new_product

@app.get("/products", response_model=List[schemas.ProductResponse])
async def list_products(db: AsyncSession = Depends(database.get_db)):
    result = await db.execute(select(database.Product))
    return result.scalars().all()
