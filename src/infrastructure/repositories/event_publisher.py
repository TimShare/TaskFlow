from typing import Any, List, Optional
from aiokafka import AIOKafkaProducer
import orjson
from core.interfaceRepositories.event_ipublisher import IEventPublisher


class AioKafkaEventPublisher(IEventPublisher):
    """
    Реализация издателя событий в Kafka с использованием aiokafka.
    Использует orjson для сериализации событий в JSON.
    """

    def __init__(self, bootstrap_servers: List[str]):
        """
        Инициализация издателя.

        :param bootstrap_servers: Список адресов Kafka брокеров (например, ["kafka:9092"]).
        """
        self._bootstrap_servers = bootstrap_servers
        self._producer: Optional[AIOKafkaProducer] = None

    async def start(self) -> None:
        """
        Запускает Kafka Producer. Должен быть вызван перед публикацией.
        """
        if self._producer is None:
            self._producer = AIOKafkaProducer(
                bootstrap_servers=self._bootstrap_servers,
                # Сериализатор для ключей (если нужны ключи для партицирования)
                # key_serializer=lambda key: orjson.dumps(key),
                # Сериализатор для значений (сообщений)
                value_serializer=lambda value: orjson.dumps(value),
            )
            await self._producer.start()
            print("AIOKafkaProducer started.")

    async def stop(self) -> None:
        """
        Останавливает Kafka Producer. Должен быть вызван при завершении работы приложения.
        """
        if self._producer is not None:
            await self._producer.stop()
            print("AIOKafkaProducer stopped.")
            self._producer = None

    async def publish_event(self, event: Any, topic: str) -> None:
        """
        Опубликовать событие в указанный топик Kafka.

        Событие сериализуется в JSON.

        :param event: Объект события (dataclass, dict и т.п.).
        :param topic: Топик Kafka для публикации.
        """
        if self._producer is None:
            # Это должно быть предотвращено корректным жизненным циклом приложения,
            # где start() вызывается при старте, а stop() при шатдауне.
            raise RuntimeError("Kafka producer is not started. Call .start() first.")

        # orjson.dumps() автоматически обрабатывает dataclasses, dicts, lists, UUIDs, datetime, enums
        # message_bytes = orjson.dumps(event) # value_serializer делает это за нас

        try:
            # producer.send_and_wait() отправляет сообщение и ждет подтверждения от брокера
            # Это может блокировать, но гарантирует, что сообщение принято брокером.
            # Для очень высокопроизводительных сценариев можно использовать producer.send() без await
            # и обрабатывать результат через Future. Но send_and_wait() проще для начала.
            await self._producer.send_and_wait(
                topic, event
            )  # value_serializer сработает здесь
            # print(f"Event published to topic {topic}: {event}") # Осторожно с логированием чувствительных данных

        except Exception as e:
            # TODO: Реализовать более надежную обработку ошибок, логирование
            print(f"Error publishing event to topic {topic}: {e}")
            # В зависимости от требований, здесь можно попробовать повторить отправку,
            # отправить в Dead Letter Queue, или просто залогировать ошибку.
            raise  # Перевыбрасываем ошибку, чтобы вызывающий код знал о сбое публикации


# Пример использования (для иллюстрации, не для продакшена в core_service)
# В реальном приложении этот класс будет инициализирован при старте
# и передан через DI в сервисы.

# async def example_usage():
#     kafka_servers = ["localhost:9092"] # Замените на адрес вашего Kafka брокера
#     publisher = AioKafkaEventPublisher(kafka_servers)
#     await publisher.start()
#
#     try:
#         # Предполагаем, что у вас есть класс ProjectCreatedEvent где-то определен
#         from src.core.entites.core_events import ProjectCreatedEvent
#         from uuid import uuid4
#         from datetime import datetime
#
#         event = ProjectCreatedEvent(
#             project_id=uuid4(),
#             name="New Example Project",
#             timestamp=datetime.utcnow()
#         )
#         await publisher.publish(event, topic="task_events")
#         print("Example event published successfully.")
#
#     finally:
#         await publisher.stop()
#
# if __name__ == "__main__":
#     import asyncio
#     asyncio.run(example_usage())
