from abc import ABC, abstractmethod


class Adaptor(ABC):
    """
    Abstract base class for TMCC Command Base adaptors.
    Subclasses implement read() and send() for their specific source/sink.
    """

    @abstractmethod
    def read(self) -> bytes:
        """Blocking read of next 3-byte TMCC packet."""
        pass

    @abstractmethod
    def send(self, packet: bytes):
        """Send a 3-byte TMCC packet."""
        pass

    def start(self):
        """Begin listening. Override if needed."""
        pass

    def stop(self):
        """Stop listening. Override if needed."""
        pass

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()
