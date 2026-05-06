from abc import ABC, abstractmethod


class Monitor(ABC):
    """
    Abstract base class for TMCC monitors.
    Subclasses subscribe to TMCC topics and handle incoming commands.
    """

    @abstractmethod
    def monitor_subscriptions(self):
        """Set up MQTT subscriptions."""
        pass

    @abstractmethod
    def run(self):
        """Start the monitor."""
        pass
