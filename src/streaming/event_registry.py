from typing import Awaitable, Callable


class EventRegistry:
    _handlers = {}

    @classmethod
    def register(cls, topic: str, handler: Callable[[dict], Awaitable[None]]):
        cls._handlers[topic] = handler

    @classmethod
    def get_handlers(cls):
        return cls._handlers
