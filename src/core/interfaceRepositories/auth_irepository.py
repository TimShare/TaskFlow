from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from uuid import UUID
from core.entites.auth_entity import User, RefreshTokenEntity


class IUserRepository(ABC):
    """Интерфейс репозитория пользователей."""

    @abstractmethod
    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        """Получить пользователя по ID.
        :param user_id: ID пользователя.
        :return: Пользователь или None, если не найден.
        """
        pass

    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[User]:
        """Получить пользователя по email.
        :param email: Email пользователя.
        :return: Пользователь или None, если не найден.
        """
        pass

    @abstractmethod
    async def create_user(self, user: User) -> User:
        """Создать пользователя.
        :param user: Пользователь.
        :return: Созданный пользователь.
        """
        pass

    @abstractmethod
    async def update_user_fields(
        self, user_id: UUID, update_data: Dict[str, Any]
    ) -> Optional[User]:
        """Обновить поля пользователя по ID с частичными данными.
        :param user_id: ID пользователя.
        :param update_data: Данные для обновления.
        :return: Обновленный пользователь или None, если не найден.
        """
        pass

    @abstractmethod
    async def add_scopes(self, user_id: UUID, scopes: List[str]) -> User:
        """Добавить права доступа пользователю.
        :param user_id: ID пользователя.
        :param scopes: Права доступа.
        :return: Обновленный пользователь.
        """
        pass

    @abstractmethod
    async def update_scopes(self, user_id: UUID, scopes: List[str]) -> User:
        """Обновить права доступа пользователя.
        :param user_id: ID пользователя.
        :param scopes: Права доступа.
        :return: Обновленный пользователь.
        """

        pass

    @abstractmethod
    async def remove_scopes(self, user_id: UUID, scopes: List[str]) -> User:
        """Удалить права доступа у пользователя.
        :param user_id: ID пользователя.
        :param scopes: Права доступа.
        :return: Обновленный пользователь.
        """

        pass

    @abstractmethod
    async def get_user_scopes(self, user_id: UUID) -> List[str]:
        """Получить права доступа пользователя.
        :param user_id: ID пользователя.
        :return: Права доступа.
        """

        pass

    @abstractmethod
    async def update_password_hash(
        self, user_id: UUID, password_hash: str
    ) -> Optional[User]:
        """Обновить хэш пароля пользователя.
        :param user_id: ID пользователя.
        :param password_hash: Новый хэш пароля.
        :return: Обновленный пользователь или None, если не найден.
        """

        pass


class IRefreshTokenRepository(ABC):
    """Интерфейс репозитория Refresh Token (хранит активные токены)."""

    @abstractmethod
    async def create_refresh_token(
        self, token_entity: RefreshTokenEntity
    ) -> RefreshTokenEntity:
        """Создать Refresh Token.
        :param token_entity: Refresh Token.
        :return: Созданный Refresh Token.
        """

        pass

    @abstractmethod
    async def get_refresh_token_by_jti(self, jti: UUID) -> Optional[RefreshTokenEntity]:
        """Получить Refresh Token по JTI.
        :param jti: JTI токена.
        :return: Refresh Token или None, если не найден.
        """

        pass

    @abstractmethod
    async def delete_refresh_token_by_jti(self, jti: UUID) -> None:
        """Удалить Refresh Token по JTI.
        :param jti: JTI токена.
        :return: None.
        """

        pass
