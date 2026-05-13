from datetime import datetime
from tmcc.factory.tmcc_command_factory import TMCCCommandFactory
from tmcc.tmcc_enums import EngineAction

DIRECTION_ACTIONS = {
    EngineAction.FORWARD.value,
    EngineAction.REVERSE.value,
    EngineAction.TOGGLE_DIR.value
}


class Engine:
    """
    Represents the current state of a TMCC engine.
    """

    def __init__(self, engine_id: int):
        self.id = engine_id
        self.direction = 'Forward'
        self.bell = False
        self.speed = 0
        self.max_speed = 2_000_000
        self.last_command = None
        self.line_comment = ''
        self.command_timestamp = datetime.now()

    def update(self, packet: bytes, comment: str = ''):
        """
        Decode a 3-byte TMCC packet and update engine state.

        Args:
            packet (bytes): A 3-byte TMCC command packet
            comment (str): Optional line comment from source file
        """
        command = TMCCCommandFactory.decode(packet)
        action = command.action.value

        if action == EngineAction.ABSOLUTE_SPEED.value:
            self.speed = max(0, min(command.speed_value, self.max_speed))
        elif action == EngineAction.RELATIVE_SPEED.value:
            self.speed = max(0, min(self.speed + command.speed_value, self.max_speed))
        elif action in DIRECTION_ACTIONS:
            self.speed = 0
            if action == EngineAction.FORWARD.value:
                self.direction = 'Forward'
            elif action == EngineAction.REVERSE.value:
                self.direction = 'Reverse'
            elif action == EngineAction.TOGGLE_DIR.value:
                self.direction = 'Reverse' if self.direction == 'Forward' else 'Forward'
        elif action == EngineAction.RING_BELL.value:
            self.bell = not self.bell

        self.last_command = command.description
        self.line_comment = comment
        self.command_timestamp = datetime.now()

    def __repr__(self):
        return (
            f"Engine(id={self.id}, speed={self.speed}, "
            f"direction={self.direction}, bell={self.bell}, "
            f"last_command={self.last_command}, "
            f"line_comment={self.line_comment}, "
            f"command_timestamp={self.command_timestamp})"
        )
