"""API route definitions."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import ProductListResponse
from app.services import get_products, get_categories

router = APIRouter()


@router.get("/health")
def health_check():
    return {"status": "ok"}


@router.get("/products", response_model=ProductListResponse)
def list_products(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    category: str | None = Query(None),
    db: Session = Depends(get_db),
):
    return get_products(db, page=page, limit=limit, category=category)


@router.get("/categories")
def list_categories(db: Session = Depends(get_db)):
    return get_categories(db)
