class NotFoundError(Exception):
    """Ресурс не найден."""

    pass


class AlreadyExistsError(Exception):
    """Ресурс уже существует."""

    pass


class DuplicateEntryError(Exception):
    """Дублирующая запись."""

    pass


class InvalidCredentialsError(Exception):
    """Неверные учетные данные."""

    pass


class TokenExpiredError(Exception):
    """Срок действия токена истек."""

    pass


class InvalidTokenError(Exception):
    """Некорректный токен."""

    pass


class InvalidRequestError(Exception):
    """Некорректный запрос."""

    pass


class PermissionDeniedError(Exception):
    """Недостаточно прав для выполнения операции."""

    pass


class ValidationError(Exception):
    """Ошибка валидации данных."""

    pass


class DatabaseError(Exception):
    """Ошибка базы данных."""

    pass


class AuthenticationError(Exception):
    """Ошибка аутентификации."""

    pass


class PermissionError(Exception):
    """Ошибка разрешения."""

    pass
