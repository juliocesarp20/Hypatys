import logging
from typing import Annotated, Optional

from aiokafka import AIOKafkaProducer
from fastapi import Depends

from src.streaming.event_producer_service import EventProducerService
from src.streaming.kafka_settings import KafkaSettings

logger = logging.getLogger(__name__)


class KafkaProducerService(EventProducerService):
    _instance: Optional["KafkaProducerService"] = None

    def __new__(cls, settings: KafkaSettings):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance._is_initialized = False
        return cls._instance

    def __init__(self, settings: KafkaSettings):
        if self._is_initialized:
            return
        self.settings = settings
        self._producer: Optional[AIOKafkaProducer] = None
        self._is_initialized = True

    async def start(self):
        if self._producer is None:
            logger.info("Initializing Kafka producer...")
            self._producer = AIOKafkaProducer(
                bootstrap_servers=self.settings.KAFKA_BOOTSTRAP_SERVERS,
                client_id=self.settings.KAFKA_CLIENT_ID,
                security_protocol=self.settings.KAFKA_SECURITY_PROTOCOL,
                sasl_mechanism=self.settings.KAFKA_SASL_MECHANISM,
                sasl_plain_username=self.settings.KAFKA_SASL_USERNAME,
                sasl_plain_password=self.settings.KAFKA_SASL_PASSWORD,
            )
            await self._producer.start()
            logger.info("Kafka producer started.")

    async def stop(self):
        if self._producer is not None:
            logger.info("Stopping Kafka producer...")
            await self._producer.stop()
            self._producer = None
            logger.info("Kafka producer stopped.")

    async def publish(self, topic: str, message: str) -> None:
        if self._producer is None:
            raise RuntimeError("Kafka producer is not started.")
        try:
            logger.info(f"Publishing message to topic '{topic}': {message}")
            await self._producer.send_and_wait(topic, value=message.encode("utf-8"))
            logger.info("Message published successfully.")
        except Exception as e:
            logger.error(f"Failed to publish message to topic '{topic}': {e}")
            raise

    async def publish_many(self, event_list: list[tuple[str, str]]) -> None:
        if self._producer is None:
            raise RuntimeError("Kafka producer is not started.")
        try:
            for topic, message in event_list:
                logger.info(f"Publishing message to topic '{topic}': {message}")
                await self._producer.send_and_wait(topic, value=message.encode("utf-8"))
            logger.info("Batch messages published successfully.")
        except Exception as e:
            logger.error(f"Failed to publish batch messages: {e}")
            raise

    model_config = {"from_attributes": True}


async def get_kafka_producer(
    settings: KafkaSettings = Depends(KafkaSettings),
) -> KafkaProducerService:
    producer = KafkaProducerService(settings)
    await producer.start()
    return producer


KafkaProducer = Annotated[EventProducerService, Depends(get_kafka_producer)]
