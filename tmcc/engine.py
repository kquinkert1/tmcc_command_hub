from tmcc.tmcc_command import TMCC_Command


class EngineCommand(TMCC_Command):
    """
    TMCC Engine Command class for controlling individual locomotives.

    Engine commands use the following 16-bit format:
        Bits 15-14: 00 (identifies this as an engine command)
        Bits 13-7:  AAAAAAA (7-bit engine address, 1-99)
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
    """

    # Command field constants
    ACTION = 0b00  # Standard action commands
    EXTENDED = 0b01  # Extended engine commands
    RELATIVE_SPEED = 0b10  # Relative speed change
    ABSOLUTE_SPEED = 0b11  # Absolute speed setting

    # Action command data field values
    FORWARD = 0b00000  # Set forward direction
    TOGGLE_DIR = 0b00001  # Toggle direction
    REVERSE = 0b00011  # Set reverse direction
    BOOST = 0b00100  # Boost speed
    OPEN_FRONT_COUPLER = 0b00101  # Open front coupler
    OPEN_REAR_COUPLER = 0b00110  # Open rear coupler
    BRAKE = 0b00111  # Apply brake
    BLOW_HORN_1 = 0b11100  # Blow horn pattern 1
    RING_BELL = 0b11101  # Ring bell
    LETOFF = 0b11110  # Steam letoff sound
    BLOW_HORN_2 = 0b11111  # Blow horn pattern 2

    # AUX command data field values
    AUX1_OFF = 0b01000  # AUX1 off
    AUX1_OPTION_1 = 0b01001  # AUX1 option 1 (CAB AUX1 button)
    AUX1_OPTION_2 = 0b01010  # AUX1 option 2
    AUX1_ON = 0b01011  # AUX1 on
    AUX2_OFF = 0b01100  # AUX2 off
    AUX2_OPTION_1 = 0b01101  # AUX2 option 1 (CAB AUX2 button)
    AUX2_OPTION_2 = 0b01110  # AUX2 option 2
    AUX2_ON = 0b01111  # AUX2 on

    # Extended command data field values
    MOMENTUM_LOW = 0b01000  # Set momentum to low
    MOMENTUM_MEDIUM = 0b01001  # Set momentum to medium
    MOMENTUM_HIGH = 0b01010  # Set momentum to high
    SET_ADDRESS = 0b01011  # Set engine address

    # Numeric command base value
    NUMERIC_BASE = 0b10000  # Base value for numeric commands (0-9)

    # Speed constants
    MAX_ABSOLUTE_SPEED = 0x1F  # Maximum absolute speed (31)
    MIN_ABSOLUTE_SPEED = 0x00  # Minimum absolute speed (0)
    MAX_RELATIVE_SPEED = 5  # Maximum relative speed change
    MIN_RELATIVE_SPEED = -5  # Minimum relative speed change

    def build_command(self, address, command_field, data_field):
        """
        Build a 3-byte TMCC engine command packet.

        Constructs the 16-bit command word using the engine command
        bit pattern: 00 + AAAAAAA + CC + DDDDD, then prepends
        the TMCC header byte (0xFE) to form the 3-byte packet.

        Args:
            address (int): Engine ID number (1-99)
            command_field (int): 2-bit command field (0-3)
            data_field (int): 5-bit data field (0-31)

        Returns:
            bytes: 3-byte TMCC command packet (0xFE, high_byte, low_byte)

        Raises:
            ValueError: If address is outside 1-99 range
        """
        if not 1 <= address <= 99:
            raise ValueError("Engine address must be between 1 and 99")
        word = (address & 0x7F) << 7
        word |= (command_field & 0x03) << 5
        word |= (data_field & 0x1F)
        high_byte = (word >> 8) & 0xFF
        low_byte = word & 0xFF
        return bytes([self.HEADER, high_byte, low_byte])

    def send_action(self, address, action):
        """
        Send a standard action command to an engine.

        Uses command field 00 (ACTION) with the specified
        data field value to trigger engine actions like
        direction changes, horn, bell, couplers, etc.

        Args:
            address (int): Engine ID number (1-99)
            action (int): Data field value for the desired action
        """
        packet = self.build_command(address, self.ACTION, action)
        self.send(packet)

    def forward(self, address):
        """
        Set engine to forward direction.

        Args:
            address (int): Engine ID number (1-99)
        """
        self.send_action(address, self.FORWARD)

    def reverse(self, address):
        """
        Set engine to reverse direction.

        Args:
            address (int): Engine ID number (1-99)
        """
        self.send_action(address, self.REVERSE)

    def toggle_direction(self, address):
        """
        Toggle engine direction between forward and reverse.

        Args:
            address (int): Engine ID number (1-99)
        """
        self.send_action(address, self.TOGGLE_DIR)

    def boost(self, address):
        """
        Apply boost to increase engine speed.

        Args:
            address (int): Engine ID number (1-99)
        """
        self.send_action(address, self.BOOST)

    def brake(self, address):
        """
        Apply brake to slow or stop the engine.

        Args:
            address (int): Engine ID number (1-99)
        """
        self.send_action(address, self.BRAKE)

    def blow_horn_1(self, address):
        """
        Activate horn pattern 1 on the engine.

        Args:
            address (int): Engine ID number (1-99)
        """
        self.send_action(address, self.BLOW_HORN_1)

    def blow_horn_2(self, address):
        """
        Activate horn pattern 2 on the engine.

        Args:
            address (int): Engine ID number (1-99)
        """
        self.send_action(address, self.BLOW_HORN_2)

    def ring_bell(self, address):
        """
        Activate the bell on the engine.

        Args:
            address (int): Engine ID number (1-99)
        """
        self.send_action(address, self.RING_BELL)

    def letoff(self, address):
        """
        Trigger steam letoff sound on the engine.

        Args:
            address (int): Engine ID number (1-99)
        """
        self.send_action(address, self.LETOFF)

    def open_front_coupler(self, address):
        """
        Open the front coupler on the engine.

        Args:
            address (int): Engine ID number (1-99)
        """
        self.send_action(address, self.OPEN_FRONT_COUPLER)

    def open_rear_coupler(self, address):
        """
        Open the rear coupler on the engine.

        Args:
            address (int): Engine ID number (1-99)
        """
        self.send_action(address, self.OPEN_REAR_COUPLER)

    def set_absolute_speed(self, address, speed):
        """
        Set the engine to an absolute speed value.

        Speed is a value from 0 (stopped) to 31 (full speed),
        using the TMCC absolute speed command field (11).

        Args:
            address (int): Engine ID number (1-99)
            speed (int): Absolute speed value (0-31)

        Raises:
            ValueError: If speed is outside 0-31 range
        """
        if not self.MIN_ABSOLUTE_SPEED <= speed <= self.MAX_ABSOLUTE_SPEED:
            raise ValueError("Absolute speed must be between 0 and 31")
        packet = self.build_command(address, self.ABSOLUTE_SPEED, speed)
        self.send(packet)

    def set_relative_speed(self, address, change):
        """
        Change the engine speed relative to its current speed.

        Uses the TMCC relative speed command field (10).
        The change value maps as follows per the TMCC spec:
            +5 = D=0xA (fastest increase)
             0 = D=0x5 (no change)
            -5 = D=0x0 (fastest decrease)

        Args:
            address (int): Engine ID number (1-99)
            change (int): Speed change value (-5 to +5)

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
        Set the momentum level for the engine.

        Momentum simulates the inertia of a real locomotive.
        Uses the TMCC extended command field (01).

        Args:
            address (int): Engine ID number (1-99)
            level (str): Momentum level - 'low', 'medium', or 'high'

        Raises:
            ValueError: If level is not 'low', 'medium', or 'high'
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

        Numeric commands control Railsounds II features:
            0 = Halt and reset
            1 = Raise volume
            3 = Raise RPMs / Start Railsounds II
            4 = Lower volume
            5 = Shutdown sequence
            6 = Lower RPMs
            8 = Deactivate auxiliary lights / smoke
            9 = Activate auxiliary lights / smoke

        Args:
            address (int): Engine ID number (1-99)
            number (int): Numeric command (0-9)

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
        Control the AUX1 function on the engine.

        Args:
            address (int): Engine ID number (1-99)
            state (str): AUX1 state - 'off', 'option1', 'option2', or 'on'

        Raises:
            ValueError: If state is not a valid AUX1 state
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
        Control the AUX2 function on the engine.
        AUX2 typically controls headlight illumination.

        Args:
            address (int): Engine ID number (1-99)
            state (str): AUX2 state - 'off', 'option1', 'option2', or 'on'

        Raises:
            ValueError: If state is not a valid AUX2 state
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
        