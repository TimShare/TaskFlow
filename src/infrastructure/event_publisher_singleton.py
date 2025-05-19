from infrastructure.repositories.event_publisher import AioKafkaEventPublisher
from settings import get_settings

config = get_settings()
event_publisher = AioKafkaEventPublisher(config.kafka_servers)
