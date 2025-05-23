from datetime import datetime, timezone
import uuid
from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy import UUID as SQLUUID


def utc_now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


class BaseModelMixin:
    id: Mapped[uuid.UUID] = mapped_column(
        SQLUUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(nullable=False, default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        nullable=False, default=utc_now, onupdate=utc_now
    )
