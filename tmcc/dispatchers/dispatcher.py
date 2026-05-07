from abc import ABC, abstractmethod


class Dispatcher(ABC):
    """
    Abstract base class for TMCC command dispatchers.
    Reads packets from an Adaptor, decodes them, and publishes to subscribers.
    """

    def __init__(self):
        self._adaptor = None
        self._subscribers = []

    @abstractmethod
    def create_adaptor(self):
        """Create and return the adaptor instance."""
        pass

    @abstractmethod
    def read(self) -> bytes:
        """Read next raw packet from the adaptor."""
        pass

    @abstractmethod
    def send(self, packet: bytes):
        """Send a raw packet via the adaptor."""
        pass

    @abstractmethod
    def publish(self, command):
        """Publish a decoded command to all subscribers."""
        pass

    def subscribe(self, callback):
        """Register a callback to receive decoded commands."""
        self._subscribers.append(callback)

    def unsubscribe(self, callback):
        """Remove a previously registered callback."""
        self._subscribers.remove(callback)

        