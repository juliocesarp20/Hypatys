import json
import logging
from abc import ABC, abstractmethod
from typing import Callable, Dict

logger = logging.getLogger(__name__)


class EventConsumerService(ABC):
    def __init__(self, **kwargs):
        pass

    @abstractmethod
    async def start(self):
        pass

    @abstractmethod
    async def consume(self):
        pass

    @abstractmethod
    async def stop(self):
        pass
