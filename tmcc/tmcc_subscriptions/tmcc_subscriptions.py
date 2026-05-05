import json
import logging
import paho.mqtt.client as mqtt

log = logging.getLogger(__name__)


class TMCCSubscriptions:
    """
    Wraps paho-mqtt client for TMCC pub/sub communication.
    Manages connection, publishing, and subscriptions.
    """

    DEFAULT_HOST = 'localhost'
    DEFAULT_PORT = 1883

    def __init__(self, host: str = DEFAULT_HOST, port: int = DEFAULT_PORT):
        self._host = host
        self._port = port
        self._client = mqtt.Client()
        self._client.on_connect = self._on_connect
        self._client.on_disconnect = self._on_disconnect
        self._client.on_message = self._on_message

    def connect(self):
        """Connect to the MQTT broker."""
        log.debug(f"Connecting to MQTT broker at {self._host}:{self._port}")
        self._client.connect(self._host, self._port)
        self._client.loop_start()

    def disconnect(self):
        """Disconnect from the MQTT broker."""
        log.debug("Disconnecting from MQTT broker")
        self._client.loop_stop()
        self._client.disconnect()

    def publish(self, topic: str, payload: dict):
        """Publish a dict payload as JSON to a topic."""
        self._client.publish(topic, json.dumps(payload))
        log.debug(f"Published to {topic}: {payload}")

    def subscribe(self, topic: str, callback):
        """Subscribe to a topic with a callback."""
        self._client.subscribe(topic)
        self._client.message_callback_add(topic, callback)
        log.debug(f"Subscribed to {topic}")

    def unsubscribe(self, topic: str):
        """Unsubscribe from a topic."""
        self._client.unsubscribe(topic)
        self._client.message_callback_remove(topic)
        log.debug(f"Unsubscribed from {topic}")

    def _on_connect(self, client, userdata, flags, rc):
        log.info(f"Connected to MQTT broker with result code {rc}")

    def _on_disconnect(self, client, userdata, rc):
        log.info(f"Disconnected from MQTT broker with result code {rc}")

    def _on_message(self, client, userdata, message):
        log.debug(f"Message received on {message.topic}: {message.payload}")

