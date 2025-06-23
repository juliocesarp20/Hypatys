from abc import ABC, abstractmethod


class EventProducerService(ABC):
    @abstractmethod
    async def publish(self, topic: str, message: str) -> None:
        pass

    @abstractmethod
    async def publish_many(self, event_list: list[tuple[str, str]]) -> None:
        pass
