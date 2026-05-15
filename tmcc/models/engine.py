import logging
import time
from datetime import datetime
from tmcc.tmcc_enums import EngineAction

DIRECTION_ACTIONS = {
    EngineAction.FORWARD.value,
    EngineAction.REVERSE.value,
    EngineAction.TOGGLE_DIR.value
}

DEFAULT_MAX_SPEED = None
DEBOUNCE_INTERVAL = 0.25  # seconds

log = logging.getLogger(__name__)


class Engine:
    """
    Represents the current state of a TMCC engine.
    """

    def __init__(self, engine_id: int):
        self.id = engine_id
        self.direction = 'Forward'
        self.bell = False
        self.speed = 0
        self.max_speed = DEFAULT_MAX_SPEED
        self.priority = 'normal'
        self.last_command = None
        self.command = None
        self.line_comment = ''
        self.command_timestamp = datetime.now()
        self._last_direction_time = 0
        self._last_bell_time = 0

    def update(self, packet: bytes, comment: str = ''):
        """
        Decode a 3-byte TMCC packet and update engine state.

        Args:
            packet (bytes): A 3-byte TMCC command packet
            comment (str): Optional line comment from source file
        """
        from tmcc.factory.tmcc_command_factory import TMCCCommandFactory
        command = TMCCCommandFactory.decode(packet)
        action = command.action.value

        if action == EngineAction.ABSOLUTE_SPEED.value:
            self._handle_absolute_speed(command.speed_value)
        elif action == EngineAction.RELATIVE_SPEED.value:
            self._handle_relative_speed(command.speed_value)
        elif action in DIRECTION_ACTIONS:
            self._handle_direction(action)
        elif action == EngineAction.RING_BELL.value:
            self._handle_bell()

        self.last_command = command.description
        self.command = command.description
        self.line_comment = comment
        self.command_timestamp = datetime.now()

    def sync_from_payload(self, payload: dict):
        """Sync engine state from an MQTT payload dict."""
        self.speed = payload.get('speed', self.speed)
        self.direction = payload.get('direction', self.direction)
        self.bell = payload.get('bell', self.bell)
        self.max_speed = payload.get('max_speed', self.max_speed)
        self.last_command = payload.get('last_command', self.last_command)
        self.command = payload.get('command', self.command)
        self.line_comment = payload.get('line_comment', self.line_comment)

    def clear_command(self):
        """Null out the current command after publish interval expires."""
        self.command = None

    def _handle_absolute_speed(self, speed_value: int):
        """Set engine to an absolute speed value."""
        log.debug(f"_handle_absolute_speed(speed_value)")
        self.speed = max(0, min(speed_value, self.max_speed)) if self.max_speed is not None else max(0, speed_value)

    def _handle_relative_speed(self, speed_value: int):
        """Adjust engine speed relative to current speed."""
        self.speed = max(0, min(self.speed + speed_value, self.max_speed)) if self.max_speed is not None else max(0, self.speed + speed_value)

    def _handle_direction(self, action: str):
        """Handle direction change with debounce."""
        now = time.time()
        if now - self._last_direction_time >= DEBOUNCE_INTERVAL:
            self.speed = 0
            if action == EngineAction.FORWARD.value:
                self.direction = 'Forward'
            elif action == EngineAction.REVERSE.value:
                self.direction = 'Reverse'
            elif action == EngineAction.TOGGLE_DIR.value:
                self.direction = 'Reverse' if self.direction == 'Forward' else 'Forward'
        self._last_direction_time = now

    def _handle_bell(self):
        """Toggle bell state with debounce."""
        now = time.time()
        if now - self._last_bell_time >= DEBOUNCE_INTERVAL:
            self.bell = not self.bell
        self._last_bell_time = now

    def __repr__(self):
        return (
            f"Engine(id={self.id}, speed={self.speed}, "
            f"direction={self.direction}, bell={self.bell}, "
            f"priority={self.priority}, "
            f"last_command={self.last_command}, "
            f"command={self.command}, "
            f"line_comment={self.line_comment}, "
            f"command_timestamp={self.command_timestamp})"
        )
