"""Pydantic schemas for request/response validation."""

import uuid
from datetime import datetime
from pydantic import BaseModel


class ProductOut(BaseModel):
    id: uuid.UUID
    name: str
    category: str
    price: float
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ProductListResponse(BaseModel):
    products: list[ProductOut]
    total_count: int
    page: int
    total_pages: int
