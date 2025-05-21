from dataclasses import dataclass, field
from uuid import UUID, uuid4
from datetime import datetime
from typing import Optional, List
from core.entites.base_entity import BaseEntity


@dataclass(kw_only=True)
class Role(BaseEntity):
    """Сущность для хранения информации о ролях пользователей."""
    name: str
    description: Optional[str] = None


@dataclass(kw_only=True)
class User(BaseEntity):
    """Сущность для хранения информации о пользователе."""
    username: str
    email: str
    password_hash: str  
    is_active: bool = True
    is_superuser: bool = False
    scopes: List[str] = field(default_factory=list)  


@dataclass(kw_only=True)
class RefreshTokenEntity(BaseEntity):
    """Сущность для хранения информации о Refresh Token на бэкенде."""
    user_id: UUID  
    jti: UUID  
    token_hash: str  
    expires_at: datetime


