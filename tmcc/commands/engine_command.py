from tmcc.commands.tmcc_command import TMCC_Command


class EngineCommand(TMCC_Command):
    """
    TMCC Engine Command class for controlling individual locomotives.

    Engine commands use the following 16-bit format:
        Bits 15-14: 00 (identifies this as an engine command)
        Bits 13-7:  AAAAAAA (7-bit engine address, 0-99)
        Bits 6-5:   CC (command field)
        Bits 4-0:   DDDDD (data field)

    Command field values:
        00 = Action command
        01 = Extended command
        10 = Relative speed
        11 = Absolute speed

    Supports all engine commands from the TMCC spec including:
        - Direction control (forward, reverse, toggle)
        - Speed control (absolute 0-31, relative -5 to +5)
        - Sound commands (horn, bell, letoff)
        - Coupler control (front and rear)
        - Boost and brake
        - Numeric keypad commands (volume, RPMs, smoke, etc.)
        - Extended commands (momentum, address assignment)
        - YOP keepalive (Engine 0 AUX1 Option 1)
    """

    # Command field constants
    ACTION = 0b00
    EXTENDED = 0b01
    RELATIVE_SPEED = 0b10
    ABSOLUTE_SPEED = 0b11

    # Action command data field values
    FORWARD = 0b00000
    TOGGLE_DIR = 0b00001
    REVERSE = 0b00011
    BOOST = 0b00100
    OPEN_FRONT_COUPLER = 0b00101
    OPEN_REAR_COUPLER = 0b00110
    BRAKE = 0b00111
    BLOW_HORN_1 = 0b11100
    RING_BELL = 0b11101
    LETOFF = 0b11110
    BLOW_HORN_2 = 0b11111

    # AUX command data field values
    AUX1_OFF = 0b01000
    AUX1_OPTION_1 = 0b01001
    AUX1_OPTION_2 = 0b01010
    AUX1_ON = 0b01011
    AUX2_OFF = 0b01100
    AUX2_OPTION_1 = 0b01101
    AUX2_OPTION_2 = 0b01110
    AUX2_ON = 0b01111

    # Extended command data field values
    MOMENTUM_LOW = 0b01000
    MOMENTUM_MEDIUM = 0b01001
    MOMENTUM_HIGH = 0b01010
    SET_ADDRESS = 0b01011

    # Numeric command base value
    NUMERIC_BASE = 0b10000

    # Speed constants
    MAX_ABSOLUTE_SPEED = 0x1F
    MIN_ABSOLUTE_SPEED = 0x00
    MAX_RELATIVE_SPEED = 5
    MIN_RELATIVE_SPEED = -5

    # Keepalive
    YOP = AUX1_OPTION_1  # Engine 0 AUX1 Option 1

    @classmethod
    def build_command(cls, address, command_field, data_field) -> bytes:
        """
        Build a 3-byte TMCC engine command packet.

        Args:
            address (int): Engine ID number (0-99)
            command_field (int): 2-bit command field (0-3)
            data_field (int): 5-bit data field (0-31)

        Returns:
            bytes: 3-byte TMCC command packet (0xFE, high_byte, low_byte)

        Raises:
            ValueError: If address is outside 0-99 range
        """
        if not 0 <= address <= 99:
            raise ValueError("Engine address must be between 0 and 99")
        word = (address & 0x7F) << 7
        word |= (command_field & 0x03) << 5
        word |= (data_field & 0x1F)
        high_byte = (word >> 8) & 0xFF
        low_byte = word & 0xFF
        return bytes([cls.HEADER, high_byte, low_byte])

    @classmethod
    def yop(cls) -> bytes:
        """Return the YOP keepalive packet (Engine 0 AUX1 Option 1)."""
        return cls.build_command(0, cls.ACTION, cls.YOP)

    def send_action(self, address, action):
        """Send a standard action command to an engine."""
        packet = self.build_command(address, self.ACTION, action)
        self.send(packet)

    def forward(self, address):
        """Set engine to forward direction."""
        self.send_action(address, self.FORWARD)

    def reverse(self, address):
        """Set engine to reverse direction."""
        self.send_action(address, self.REVERSE)

    def toggle_direction(self, address):
        """Toggle engine direction between forward and reverse."""
        self.send_action(address, self.TOGGLE_DIR)

    def boost(self, address):
        """Apply boost to increase engine speed."""
        self.send_action(address, self.BOOST)

    def brake(self, address):
        """Apply brake to slow or stop the engine."""
        self.send_action(address, self.BRAKE)

    def blow_horn_1(self, address):
        """Activate horn pattern 1 on the engine."""
        self.send_action(address, self.BLOW_HORN_1)

    def blow_horn_2(self, address):
        """Activate horn pattern 2 on the engine."""
        self.send_action(address, self.BLOW_HORN_2)

    def ring_bell(self, address):
        """Activate the bell on the engine."""
        self.send_action(address, self.RING_BELL)

    def letoff(self, address):
        """Trigger steam letoff sound on the engine."""
        self.send_action(address, self.LETOFF)

    def open_front_coupler(self, address):
        """Open the front coupler on the engine."""
        self.send_action(address, self.OPEN_FRONT_COUPLER)

    def open_rear_coupler(self, address):
        """Open the rear coupler on the engine."""
        self.send_action(address, self.OPEN_REAR_COUPLER)

    def set_absolute_speed(self, address, speed):
        """
        Set the engine to an absolute speed value (0-31).

        Raises:
            ValueError: If speed is outside 0-31 range
        """
        if not self.MIN_ABSOLUTE_SPEED <= speed <= self.MAX_ABSOLUTE_SPEED:
            raise ValueError("Absolute speed must be between 0 and 31")
        packet = self.build_command(address, self.ABSOLUTE_SPEED, speed)
        self.send(packet)

    def set_relative_speed(self, address, change):
        """
        Change the engine speed relative to its current speed (-5 to +5).

        Raises:
            ValueError: If change is outside -5 to +5 range
        """
        if not self.MIN_RELATIVE_SPEED <= change <= self.MAX_RELATIVE_SPEED:
            raise ValueError("Relative speed change must be between -5 and +5")
        data = change + 5
        packet = self.build_command(address, self.RELATIVE_SPEED, data)
        self.send(packet)

    def set_momentum(self, address, level):
        """
        Set the momentum level for the engine ('low', 'medium', or 'high').

        Raises:
            ValueError: If level is not valid
        """
        levels = {
            'low': self.MOMENTUM_LOW,
            'medium': self.MOMENTUM_MEDIUM,
            'high': self.MOMENTUM_HIGH
        }
        if level not in levels:
            raise ValueError("Momentum level must be 'low', 'medium', or 'high'")
        packet = self.build_command(address, self.EXTENDED, levels[level])
        self.send(packet)

    def numeric_command(self, address, number):
        """
        Send a numeric keypad command (0-9) to the engine.

        Raises:
            ValueError: If number is outside 0-9 range
        """
        if not 0 <= number <= 9:
            raise ValueError("Numeric command must be between 0 and 9")
        data = self.NUMERIC_BASE | number
        packet = self.build_command(address, self.ACTION, data)
        self.send(packet)

    def aux1(self, address, state):
        """
        Control the AUX1 function ('off', 'option1', 'option2', or 'on').

        Raises:
            ValueError: If state is not valid
        """
        states = {
            'off': self.AUX1_OFF,
            'option1': self.AUX1_OPTION_1,
            'option2': self.AUX1_OPTION_2,
            'on': self.AUX1_ON
        }
        if state not in states:
            raise ValueError("AUX1 state must be 'off', 'option1', 'option2', or 'on'")
        self.send_action(address, states[state])

    def aux2(self, address, state):
        """
        Control the AUX2 function ('off', 'option1', 'option2', or 'on').

        Raises:
            ValueError: If state is not valid
        """
        states = {
            'off': self.AUX2_OFF,
            'option1': self.AUX2_OPTION_1,
            'option2': self.AUX2_OPTION_2,
            'on': self.AUX2_ON
        }
        if state not in states:
            raise ValueError("AUX2 state must be 'off', 'option1', 'option2', or 'on'")
        self.send_action(address, states[state])