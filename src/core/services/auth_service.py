from datetime import datetime, timedelta, timezone
from typing import List, Optional, Dict, Any
from uuid import UUID, uuid4
from core.entites.auth_entity import User, RefreshTokenEntity
from core.interfaceRepositories.auth_irepository import (
    IUserRepository,
    IRefreshTokenRepository,
)
from core.exceptions import (
    DuplicateEntryError,
    NotFoundError,
    AuthenticationError,
    PermissionError,
)
from settings import get_settings
from passlib.context import CryptContext
import jwt

# Импортируем DTO для токенов
from core.entites.auth_dtos import (
    TokenPairData,
    AccessTokenData,
    RefreshTokenData,
    TokenPayload,
)


settings = get_settings()


class AuthService:
    def __init__(
        self,
        user_repository: IUserRepository,
        refresh_token_repository: IRefreshTokenRepository,
    ):
        """
        Инициализация AuthService.

        :param user_repository: Репозиторий для работы с пользователями.
        :param refresh_token_repository: Репозиторий для хранения Refresh Token.
        """
        self._user_repo: IUserRepository = user_repository
        self._refresh_token_repo: IRefreshTokenRepository = refresh_token_repository
        self._pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

        self._jwt_algorithm = settings.algorithm
        self._jwt_secret_key = settings.secret_key
        self._access_token_expire = timedelta(
            minutes=settings.access_token_expire_minutes
        )
        self._refresh_token_expire = timedelta(days=settings.refresh_token_expire_days)

    async def create_user(self, user_data: User) -> User:
        """
        Создать нового пользователя.
        """
        # ВАЖНО: Предполагается, что user_data.password_hash уже содержит хеш пароля
        # Если на вход в API приходит UserCreateDTO с сырым паролем, хеширование должно происходить
        # либо в API-слое перед вызовом сервиса, либо в отдельном методе сервиса create_user_with_password.
        # В данном примере предполагается, что user_data.password_hash УЖЕ хеш.
        if not user_data.password_hash:
            raise ValueError(
                "Password hash must be provided when creating a user entity"
            )

        if await self._user_repo.get_by_email(email=user_data.email):
            raise DuplicateEntryError(
                f"User with email '{user_data.email}' already exists"
            )

        created_user = await self._user_repo.create_user(user_data)
        return created_user

    async def get_user(self, user_id: UUID) -> User:
        """
        Получить пользователя по ID.
        """
        user = await self._user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundError(f"User with ID {user_id} not found")
        return user

    async def get_user_by_email(self, email: str) -> User:
        """
        Получить пользователя по email.
        """
        user = await self._user_repo.get_by_email(email)
        if not user:
            raise NotFoundError(f"User with email '{email}' not found")
        return user

    async def update_user_fields(
        self, user_id: UUID, update_data: Dict[str, Any]
    ) -> User:  # Тип UUID, принимаем dict для обновления
        """
        Обновить существующего пользователя по ID с частичными данными.
        Не предназначен для смены пароля или управления скоупами - используйте отдельные методы.
        """
        if update_data.get("hash_password"):
            raise ValueError("Use dedicated method to update password.")

        if "password_hash" in update_data or "scopes" in update_data:
            raise ValueError("Use dedicated methods to update password or scopes.")

        updated_user = await self._user_repo.update_user_fields(user_id, update_data)
        if not updated_user:
            raise NotFoundError(f"User with ID {user_id} not found")
        return updated_user

    async def change_password(
        self, user_id: UUID, old_password: str, new_password: str
    ) -> User:
        """
        Изменить пароль пользователя.
        """
        user = await self.get_user(
            user_id
        )  # Используем метод сервиса для получения пользователя

        if not self._pwd_context.verify(old_password, user.password_hash):
            raise AuthenticationError("Invalid old password")

        new_password_hash = self._pwd_context.hash(new_password)

        updated_user = await self._user_repo.update_password_hash(
            user_id, new_password_hash
        )

        # В реальном приложении здесь также стоит отозвать все рефреш-токены пользователя
        # await self._refresh_token_repo.delete_all_refresh_tokens_for_user(user_id) # TODO: Добавить такой метод в репозиторий

        if not updated_user:
            raise NotFoundError(f"Failed to update password for user {user_id}")

        return updated_user

    async def login(self, email: str, password: str) -> TokenPairData:  # Возвращает DTO
        """
        Аутентифицирует пользователя и выпускает новую пару токенов (Access и Refresh).
        """
        try:
            user = await self.get_user_by_email(email)
        except NotFoundError:
            raise AuthenticationError("Invalid email or password")

        if not self._pwd_context.verify(password, user.password_hash):
            raise AuthenticationError("Invalid email or password")

        access_claims = {
            "sub": str(user.id),
            "scopes": user.scopes,
            "is_superuser": user.is_superuser,
            "type": "access",
            "jti": str(uuid4()),
        }
        refresh_claims = {
            "sub": str(user.id),
            "type": "refresh",
            "jti": str(uuid4()),
        }

        access_token_string, access_expires_at = self._create_jwt(
            access_claims, self._access_token_expire
        )
        refresh_token_string, refresh_expires_at = self._create_jwt(
            refresh_claims, self._refresh_token_expire
        )

        refresh_token_jti_uuid = UUID(refresh_claims["jti"])
        refresh_token_entity = RefreshTokenEntity(
            user_id=user.id,
            jti=refresh_token_jti_uuid,
            token_hash=self._pwd_context.hash(refresh_token_string),
            expires_at=refresh_expires_at,
        )
        await self._refresh_token_repo.create_refresh_token(refresh_token_entity)

        return TokenPairData(
            access_token=AccessTokenData(
                token=access_token_string, expires_at=access_expires_at
            ),
            refresh_token=RefreshTokenData(
                token=refresh_token_string,
                jti=refresh_token_jti_uuid,
                expires_at=refresh_expires_at,
            ),
        )

    async def logout(self, refresh_token_string: str) -> None:
        """
        Завершает сессию пользователя, отзывая Refresh Token.
        """
        try:

            payload = jwt.decode(
                refresh_token_string,
                self._jwt_secret_key,
                algorithms=[self._jwt_algorithm],
                options={"verify_exp": False},
            )
            jti_str: Optional[str] = payload.get("jti")
            token_type: Optional[str] = payload.get("type")

            if token_type != "refresh" or not jti_str:
                print(
                    f"Warning: Logout attempt with invalid token type or missing JTI: {payload}"
                )
                raise AuthenticationError("Invalid refresh token format")

            jti = UUID(jti_str)

            await self._refresh_token_repo.delete_refresh_token_by_jti(jti)

        except (jwt.PyJWTError, ValueError) as e:
            print(f"Warning: Attempted logout with invalid JWT or UUID format: {e}")
            pass

    async def refresh_tokens(self, refresh_token_string: str) -> TokenPairData:
        """
        Обновляет пару Access/Refresh токенов, используя валидный Refresh Token.
        Отозывает старый Refresh Token и выпускает новую пару.
        """
        try:
            payload = jwt.decode(
                refresh_token_string,
                self._jwt_secret_key,
                algorithms=[self._jwt_algorithm],
                options={"verify_exp": True},
            )

            jti_str: Optional[str] = payload.get("jti")
            sub_str: Optional[str] = payload.get("sub")
            token_type: Optional[str] = payload.get("type")

            if token_type != "refresh" or not jti_str or not sub_str:
                print(f"Warning: Refresh attempt with invalid token payload: {payload}")
                raise AuthenticationError("Invalid refresh token format")

            jti = UUID(jti_str)
            user_id = UUID(sub_str)

            refresh_token_entity = (
                await self._refresh_token_repo.get_refresh_token_by_jti(jti)
            )

            if refresh_token_entity is None:
                print(
                    f"Warning: Refresh token with jti {jti} not found or expired in repository."
                )
                raise AuthenticationError("Invalid or expired refresh token")

            if not self._pwd_context.verify(
                refresh_token_string, refresh_token_entity.token_hash
            ):
                print(f"Warning: Refresh token hash mismatch for jti {jti}.")
                raise AuthenticationError("Invalid refresh token")

            user = await self._user_repo.get_by_id(user_id)
            if user is None or not user.is_active:
                print(
                    f"Warning: User {user_id} not found or inactive for refresh token jti {jti}."
                )
                await self._refresh_token_repo.delete_refresh_token_by_jti(jti)
                raise AuthenticationError("User not found or inactive")

            await self._refresh_token_repo.delete_refresh_token_by_jti(jti)
            print(f"Old refresh token with jti {jti} deleted during refresh.")

            new_access_claims = {
                "sub": str(user.id),
                "scopes": user.scopes,
                "is_superuser": user.is_superuser,
                "type": "access",
                "jti": str(uuid4()),
            }
            new_refresh_claims = {
                "sub": str(user.id),
                "type": "refresh",
                "jti": str(uuid4()),
            }

            new_access_token_string, new_access_expires_at = self._create_jwt(
                new_access_claims, self._access_token_expire
            )
            new_refresh_token_string, new_refresh_expires_at = self._create_jwt(
                new_refresh_claims, self._refresh_token_expire
            )

            new_refresh_token_jti_uuid = UUID(new_refresh_claims["jti"])
            new_refresh_token_entity = RefreshTokenEntity(
                user_id=user.id,
                jti=new_refresh_token_jti_uuid,
                token_hash=self._pwd_context.hash(new_refresh_token_string),
                expires_at=new_refresh_expires_at,
            )
            await self._refresh_token_repo.create_refresh_token(
                new_refresh_token_entity
            )  #

            return TokenPairData(
                access_token=AccessTokenData(
                    token=new_access_token_string, expires_at=new_access_expires_at
                ),
                refresh_token=RefreshTokenData(
                    token=new_refresh_token_string,
                    jti=new_refresh_token_jti_uuid,
                    expires_at=new_refresh_expires_at,
                ),
            )

        except jwt.ExpiredSignatureError:
            print("Warning: Expired refresh token provided during refresh.")
            raise AuthenticationError("Refresh token expired")
        except (jwt.PyJWTError, ValueError) as e:
            print(f"Warning: Invalid JWT or UUID format during refresh attempt: {e}")
            raise AuthenticationError("Invalid token provided")
        except NotFoundError as e:
            raise AuthenticationError(str(e))

    def _create_jwt(
        self, claims: Dict[str, Any], expires_delta: timedelta
    ) -> tuple[str, datetime]:
        """
        Создает JWT токен с заданными claims и сроком действия.
        Возвращает строку токена и абсолютное время истечения.
        """
        to_encode = claims.copy()
        expire_at = datetime.now(timezone.utc) + expires_delta

        encoded_jwt = jwt.encode(
            to_encode, self._jwt_secret_key, algorithm=self._jwt_algorithm
        )
        return encoded_jwt, expire_at

    async def verify_access_token(self, token_string: str) -> Optional[TokenPayload]:
        """
        Валидирует Access Token (JWT).
        Проверяет подпись, срок действия, тип токена и наличие обязательных claims.
        НЕ ПРОВЕРЯЕТ существование пользователя в базе данных.
        Возвращает DTO с данными пейлоада, если токен валиден, иначе None.
        """
        try:
            payload_data = jwt.decode(
                token_string,
                self._jwt_secret_key,
                algorithms=[self._jwt_algorithm],
                options={"verify_exp": True},
            )

            if (
                payload_data.get("type") != "access"
                or not payload_data.get("sub")
                or not payload_data.get("jti")
            ):
                print(
                    f"Warning: Access token payload missing required claims or wrong type: {payload_data}"
                )
                return None

            payload_sub_uuid = UUID(payload_data["sub"])
            payload_jti_uuid = UUID(payload_data["jti"])
            payload_exp_datetime = datetime.fromtimestamp(
                payload_data["exp"], tz=timezone.utc
            )
            return TokenPayload(
                sub=payload_sub_uuid,
                exp=payload_exp_datetime,
                jti=payload_jti_uuid,
                type=payload_data["type"],
                scopes=payload_data.get("scopes", []),
                is_superuser=payload_data.get("is_superuser", False),
            )

        except jwt.ExpiredSignatureError:
            print("Warning: Access token expired.")
            return None
        except jwt.PyJWTError as e:
            print(f"Warning: Invalid access token: {e}")
            return None
        except (ValueError, TypeError) as e:
            print(
                f"Warning: Access token payload has invalid format (UUID/type conversion): {e}"
            )
            return None

    async def add_scopes(self, user_id: UUID, scopes: List[str]) -> User:
        """Добавляет новые права пользователю."""
        existing_user = await self._user_repo.get_by_id(user_id)
        if not existing_user:
            raise NotFoundError(f"User with ID {user_id} not found")
        return await self._user_repo.add_scopes(user_id, scopes)

    async def update_scopes(self, user_id: UUID, scopes: List[str]) -> User:
        """Полностью заменяет права пользователя."""
        return await self._user_repo.update_scopes(user_id, scopes)

    async def remove_scopes(self, user_id: UUID, scopes: List[str]) -> User:
        """Удаляет указанные права у пользователя."""
        return await self._user_repo.remove_scopes(user_id, scopes)

    async def get_user_scopes(self, user_id: UUID) -> List[str]:
        """Получает текущие права пользователя."""
        return await self._user_repo.get_user_scopes(user_id)
