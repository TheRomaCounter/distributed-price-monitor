from datetime import datetime
from pydantic import BaseModel, HttpUrl

class ProductCreate(BaseModel):
    url: HttpUrl

class PriceHistoryResponse(BaseModel):
    id: int
    price: float
    recorded_at: datetime

    class Config:
        from_attributes = True

class ProductResponse(BaseModel):
    id: int
    title: str
    url: str
    current_price: float
    created_at: datetime

    class Config:
        from_attributes = True
