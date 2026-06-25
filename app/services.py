"""Business logic for product browsing with keyset pagination."""

import uuid
import base64
import json
from datetime import datetime
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from app.models import Product


def encode_cursor(created_at: datetime, product_id: uuid.UUID) -> str:
    """Encode (created_at, id) into an opaque base64 cursor string."""
    payload = {
        "created_at": created_at.isoformat(),
        "id": str(product_id),
    }
    return base64.urlsafe_b64encode(json.dumps(payload).encode()).decode()


def decode_cursor(cursor: str) -> tuple[datetime, uuid.UUID]:
    """Decode a cursor string back into (created_at, id)."""
    payload = json.loads(base64.urlsafe_b64decode(cursor.encode()))
    return (
        datetime.fromisoformat(payload["created_at"]),
        uuid.UUID(payload["id"]),
    )


def get_products(
    db: Session,
    page: int = 1,
    limit: int = 20,
    category: str | None = None,
) -> dict:
    """
    Fetch products using offset-based pagination.
    Supports specific page jumping.
    """
    # Cap limit to prevent abuse
    limit = min(limit, 100)

    query = select(Product)

    # Apply category filter
    if category:
        query = query.where(Product.category == category)

    # Get total count
    total_count = db.scalar(select(func.count()).select_from(query.subquery()))

    # Apply offset and limit
    query = query.order_by(Product.created_at.desc(), Product.id.desc())
    query = query.offset((page - 1) * limit).limit(limit)

    products = db.execute(query).scalars().all()
    total_pages = (total_count + limit - 1) // limit if limit > 0 else 0

    return {
        "products": products,
        "total_count": total_count,
        "page": page,
        "total_pages": total_pages,
    }


def get_categories(db: Session) -> list[str]:
    """Return all distinct product categories, sorted alphabetically."""
    result = db.execute(
        select(Product.category).distinct().order_by(Product.category)
    )
    return [row[0] for row in result]
