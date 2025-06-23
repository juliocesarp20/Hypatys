import asyncio
import json
import logging
from typing import Callable, Dict

from aiokafka import AIOKafkaConsumer

from src.streaming.event_consumer_service import EventConsumerService
from src.streaming.event_registry import EventRegistry
from src.streaming.kafka_settings import KafkaSettings

logger = logging.getLogger(__name__)


class KafkaConsumerService(EventConsumerService):
    def __init__(self, settings: KafkaSettings, poll_interval: int = 10):
        self.settings = settings
        self.consumer = None
        self.running = True
        self.poll_interval = poll_interval

    def _get_topic_handlers(self) -> Dict[str, Callable]:
        """Fetch the topic handlers from EventRegistry."""
        return EventRegistry.get_handlers()

    async def _update_topics(self):
        if not self.consumer:
            return

        current_topics = set(self.consumer.subscription())
        new_topics = set(list(self._get_topic_handlers().keys()))

        if current_topics != new_topics:
            logger.info(
                f"Updating topics. Current: {current_topics}, New: {new_topics}"
            )
            await self.consumer.unsubscribe()
            await self.consumer.subscribe(list(new_topics))

    async def start(self):
        """Start the Kafka consumer."""
        topic_handlers = self._get_topic_handlers()
        topics = list(topic_handlers.keys())

        logger.info(f"Starting Kafka consumer for topics: {topics}")
        self.consumer = AIOKafkaConsumer(
            *topics,
            bootstrap_servers=self.settings.KAFKA_BOOTSTRAP_SERVERS,
            group_id=self.settings.KAFKA_CLIENT_ID,
            security_protocol=self.settings.KAFKA_SECURITY_PROTOCOL,
            sasl_mechanism=self.settings.KAFKA_SASL_MECHANISM,
            sasl_plain_username=self.settings.KAFKA_SASL_USERNAME,
            sasl_plain_password=self.settings.KAFKA_SASL_PASSWORD,
            auto_offset_reset="earliest",
            enable_auto_commit=True,
            metadata_max_age_ms=10000,
        )
        await self.consumer.start()

    async def consume(self):
        """Consume messages from Kafka and route them to appropriate handlers."""
        logger.info("Consuming messages...")
        try:
            while self.running:
                await self._update_topics()
                async for message in self.consumer:
                    print("abcde")
                    if not self.running:
                        break

                    topic = message.topic
                    try:
                        payload = json.loads(message.value)
                        logger.info(f"Received message on topic '{topic}': {payload}")

                        topic_handlers = self._get_topic_handlers()
                        topics = list(topic_handlers.keys())
                        if topic in topics:
                            await topic_handlers[topic](payload)
                        else:
                            logger.warning(f"No handler for topic '{topic}'")
                    except Exception as e:
                        logger.error(
                            f"Error processing message on topic '{topic}': {e}"
                        )
                await asyncio.sleep(self.poll_interval)
        except Exception as e:
            logger.error(f"Error in Kafka consumer loop: {e}")
        finally:
            await self.stop()

    async def stop(self):
        """Stop the Kafka consumer."""
        if self.consumer:
            logger.info("Stopping Kafka consumer...")
            await self.consumer.stop()
        self.running = False
