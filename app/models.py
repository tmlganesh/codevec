"""SQLAlchemy models."""

import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Numeric, DateTime, Index
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class Product(Base):
    __tablename__ = "products"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=False)
    price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # --- Indexes ---
    # 1. Primary browsing query: ORDER BY created_at DESC, id DESC
    #    Enables index-only scan for keyset pagination.
    # 2. Category-filtered browsing: WHERE category = ? ORDER BY created_at DESC, id DESC
    #    Composite index lets Postgres seek directly to the category partition,
    #    then walk the (created_at, id) range without a sort step.
    __table_args__ = (
        Index("ix_products_created_at_id", created_at.desc(), id.desc()),
        Index(
            "ix_products_category_created_at_id",
            "category",
            created_at.desc(),
            id.desc(),
        ),
    )
