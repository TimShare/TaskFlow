from abc import ABC, abstractmethod
from typing import Any


class IEventPublisher(ABC):
    """Интерфейс издателя событий в Kafka."""

    @abstractmethod
    async def publish_event(self, event: Any, topic: str) -> None:
        """Опубликовать событие в Kafka."""
        pass

    @abstractmethod
    async def start(self) -> None:
        """Запустить издателя (подключиться к брокеру)."""
        pass

    @abstractmethod
    async def stop(self) -> None:
        """Остановить издателя (отключиться от брокера)."""
        pass
