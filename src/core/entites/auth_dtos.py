from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, List
from uuid import UUID


@dataclass
class AccessTokenData:
    """DTO для данных Access Token, отправляемых клиенту."""

    token: str
    expires_at: datetime
    token_type: str = "Bearer"


@dataclass
class RefreshTokenData:
    """DTO для данных Refresh Token, отправляемых клиенту."""

    token: str
    jti: UUID
    expires_at: datetime


@dataclass
class TokenPairData:
    """DTO для пары Access и Refresh токенов."""

    access_token: AccessTokenData
    refresh_token: RefreshTokenData


@dataclass
class TokenPayload:
    """DTO для данных из пейлоада валидного Access Token."""

    sub: UUID
    exp: datetime
    jti: UUID
    type: str
    scopes: List[str] = field(default_factory=list)
    is_superuser: bool = False
