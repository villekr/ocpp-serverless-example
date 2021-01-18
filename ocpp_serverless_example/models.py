from dataclasses import dataclass
from abc import ABC, abstractmethod


class Queue(ABC):
    """Queue interface for routing incoming CallResult/CallError to Call initiator."""

    @abstractmethod
    async def get(self) -> str:
        pass

    @abstractmethod
    def put_nowait(self, msg):
        pass


class Connection(ABC):
    """Connection interface for sending/receiving messages"""

    @abstractmethod
    async def send(self, message: str):
        pass

    @abstractmethod
    async def recv(self) -> str:
        pass


class ResponseStrategy(ABC):
    """Response interface for delivering CallResult/CallError to Call initiator."""

    @abstractmethod
    async def run(self, response):
        pass


class AfterHookStrategy(ABC):
    """AfterHook interface for triggering "after" processing for message."""

    @abstractmethod
    async def run(self, handler, payload):
        pass


@dataclass
class Context:
    """Context class encapsulates"""

    queue: Queue
    connection: Connection
    response_strategy: ResponseStrategy
    after_hook_strategy: AfterHookStrategy
