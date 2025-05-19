from dataclasses import dataclass, field
from datetime import datetime
from uuid import uuid4, UUID


@dataclass
class BaseEntity:
    """Базовый класс для всех сущностей."""

    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
