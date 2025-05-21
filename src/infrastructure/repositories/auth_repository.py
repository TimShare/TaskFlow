# filepath: src/infrastructure/repositories/auth_repository.py
from typing import Optional, List, Dict, Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete

from core.interfaceRepositories.auth_irepository import (
    IUserRepository,
    IRefreshTokenRepository,
)
from core.entites.auth_entity import User, RefreshTokenEntity
from infrastructure.models.auth_models import UserModel, RefreshTokenModel


class UserRepository(IUserRepository):
    """Репозиторий для работы с пользователями"""

    def __init__(self, session: AsyncSession):
        self._session = session

    @staticmethod
    def _map_to_entity(model: UserModel) -> User:
        return User(
            id=model.id,
            username=model.username,
            email=model.email,
            password_hash=model.password_hash,
            is_active=model.is_active,
            is_superuser=model.is_superuser,
            scopes=model.scopes,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    @staticmethod
    def _map_to_model(entity: User) -> UserModel:
        return UserModel(
            id=entity.id,
            username=entity.username,
            email=entity.email,
            password_hash=entity.password_hash,
            is_active=entity.is_active,
            is_superuser=entity.is_superuser,
            scopes=entity.scopes,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        result = await self._session.execute(
            select(UserModel).where(UserModel.id == user_id)
        )
        m = result.scalars().first()
        return self._map_to_entity(m) if m else None

    async def get_by_email(self, email: str) -> Optional[User]:
        result = await self._session.execute(
            select(UserModel).where(UserModel.email == email)
        )
        m = result.scalars().first()
        return self._map_to_entity(m) if m else None

    async def create_user(self, user: User) -> User:
        m = self._map_to_model(user)
        self._session.add(m)
        await self._session.commit()
        await self._session.refresh(m)
        return self._map_to_entity(m)

    async def update_user_fields(
        self, user_id: UUID, update_data: Dict[str, Any]
    ) -> Optional[User]:
        stmt = (
            update(UserModel)
            .where(UserModel.id == user_id)
            .values(**update_data)
            .execution_options(synchronize_session="fetch")
        )
        result = await self._session.execute(stmt)
        await self._session.commit()
        return await self.get_by_id(user_id) if result.rowcount > 0 else None

    async def add_scopes(self, user_id: UUID, scopes: List[str]) -> User:
        user = await self.get_by_id(user_id)
        new_scopes = list(set(user.scopes + scopes))
        return await self.update_user_fields(user_id, {"scopes": new_scopes})

    async def update_scopes(self, user_id: UUID, scopes: List[str]) -> User:
        return await self.update_user_fields(user_id, {"scopes": scopes})

    async def remove_scopes(self, user_id: UUID, scopes: List[str]) -> User:
        user = await self.get_by_id(user_id)
        new_scopes = [s for s in user.scopes if s not in scopes]
        return await self.update_user_fields(user_id, {"scopes": new_scopes})

    async def get_user_scopes(self, user_id: UUID) -> List[str]:
        user = await self.get_by_id(user_id)
        return user.scopes

    async def update_password_hash(
        self, user_id: UUID, password_hash: str
    ) -> Optional[User]:
        return await self.update_user_fields(user_id, {"password_hash": password_hash})


class RefreshTokenRepository(IRefreshTokenRepository):
    """Репозиторий для работы с refresh-токенами"""

    def __init__(self, session: AsyncSession):
        self._session = session

    async def create_refresh_token(
        self, token_entity: RefreshTokenEntity
    ) -> RefreshTokenEntity:
        m = RefreshTokenModel(
            jti=token_entity.jti,
            user_id=token_entity.user_id,
            token_hash=token_entity.token_hash,
            expires_at=token_entity.expires_at,
        )
        self._session.add(m)
        await self._session.commit()
        return token_entity

    async def get_refresh_token_by_jti(self, jti: UUID) -> Optional[RefreshTokenEntity]:
        result = await self._session.execute(
            select(RefreshTokenModel).where(RefreshTokenModel.jti == jti)
        )
        m = result.scalars().first()
        if not m:
            return None
        return RefreshTokenEntity(
            user_id=m.user_id,
            jti=m.jti,
            token_hash=m.token_hash,
            expires_at=m.expires_at,
            id=m.jti,
            created_at=m.created_at,
            updated_at=m.created_at,
        )

    async def delete_refresh_token_by_jti(self, jti: UUID) -> None:
        stmt = delete(RefreshTokenModel).where(RefreshTokenModel.jti == jti)
        await self._session.execute(stmt)
        await self._session.commit()
