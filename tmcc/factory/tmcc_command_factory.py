from tmcc.tmcc_enums import (
    CommandType,
    EngineAction,
    TrainAction,
    SwitchAction,
    RouteAction,
    AccessoryAction
)


class TMCCCommandFactory:
    """
    Factory class for decoding raw TMCC command packets.

    Receives a 3-byte TMCC packet and decodes it into a
    structured object identifying the command type, address,
    command field, data field, and a human-readable description.

    TMCC packet format:
        Byte 1: Header byte (0xFE)
        Byte 2: High byte of 16-bit command word
        Byte 3: Low byte of 16-bit command word

    Command type is determined by bits 15-14 of the 16-bit word:
        00 = Engine command
        01 = Switch or Route command
        10 = Accessory command
        11 = Train command
    """

    # Command type identifiers from bits 15-14
    ENGINE_BITS = 0b00
    SWITCH_BITS = 0b01
    ACCESSORY_BITS = 0b10
    TRAIN_BITS = 0b11

    # Engine action lookup table: (command_field, data_field) -> EngineAction
    ENGINE_ACTION_MAP = {
        (0b00, 0b00000): EngineAction.FORWARD,
        (0b00, 0b00001): EngineAction.TOGGLE_DIR,
        (0b00, 0b00011): EngineAction.REVERSE,
        (0b00, 0b00100): EngineAction.BOOST,
        (0b00, 0b00101): EngineAction.OPEN_FRONT_COUPLER,
        (0b00, 0b00110): EngineAction.OPEN_REAR_COUPLER,
        (0b00, 0b00111): EngineAction.BRAKE,
        (0b00, 0b01000): EngineAction.AUX1_OFF,
        (0b00, 0b01001): EngineAction.AUX1_OPTION_1,
        (0b00, 0b01010): EngineAction.AUX1_OPTION_2,
        (0b00, 0b01011): EngineAction.AUX1_ON,
        (0b00, 0b01100): EngineAction.AUX2_OFF,
        (0b00, 0b01101): EngineAction.AUX2_OPTION_1,
        (0b00, 0b01110): EngineAction.AUX2_OPTION_2,
        (0b00, 0b01111): EngineAction.AUX2_ON,
        (0b00, 0b10000): EngineAction.NUMERIC_0,
        (0b00, 0b10001): EngineAction.NUMERIC_1,
        (0b00, 0b10010): EngineAction.NUMERIC_2,
        (0b00, 0b10011): EngineAction.NUMERIC_3,
        (0b00, 0b10100): EngineAction.NUMERIC_4,
        (0b00, 0b10101): EngineAction.NUMERIC_5,
        (0b00, 0b10110): EngineAction.NUMERIC_6,
        (0b00, 0b10111): EngineAction.NUMERIC_7,
        (0b00, 0b11000): EngineAction.NUMERIC_8,
        (0b00, 0b11001): EngineAction.NUMERIC_9,
        (0b00, 0b11100): EngineAction.BLOW_HORN_1,
        (0b00, 0b11101): EngineAction.RING_BELL,
        (0b00, 0b11110): EngineAction.LETOFF,
        (0b00, 0b11111): EngineAction.BLOW_HORN_2,
        (0b01, 0b01000): EngineAction.MOMENTUM_LOW,
        (0b01, 0b01001): EngineAction.MOMENTUM_MEDIUM,
        (0b01, 0b01010): EngineAction.MOMENTUM_HIGH,
        (0b01, 0b01011): EngineAction.SET_ADDRESS,
    }

    # Switch action lookup table: data_field -> SwitchAction
    SWITCH_ACTION_MAP = {
        0b00000: SwitchAction.THROW_THROUGH,
        0b00001: SwitchAction.THROW_OUT,
        0b01001: SwitchAction.SET_ADDRESS,
    }

    # Accessory action lookup table: data_field -> AccessoryAction
    ACCESSORY_ACTION_MAP = {
        0b01000: AccessoryAction.AUX1_OFF,
        0b01001: AccessoryAction.AUX1_OPTION_1,
        0b01010: AccessoryAction.AUX1_OPTION_2,
        0b01011: AccessoryAction.AUX1_ON,
        0b01100: AccessoryAction.AUX2_OFF,
        0b01101: AccessoryAction.AUX2_OPTION_1,
        0b01110: AccessoryAction.AUX2_OPTION_2,
        0b01111: AccessoryAction.AUX2_ON,
    }

    # Train action lookup table mirrors engine actions
    TRAIN_ACTION_MAP = {
        (0b00, 0b00000): TrainAction.FORWARD,
        (0b00, 0b00001): TrainAction.TOGGLE_DIR,
        (0b00, 0b00011): TrainAction.REVERSE,
        (0b00, 0b00100): TrainAction.BOOST,
        (0b00, 0b00101): TrainAction.OPEN_FRONT_COUPLER,
        (0b00, 0b00110): TrainAction.OPEN_REAR_COUPLER,
        (0b00, 0b00111): TrainAction.BRAKE,
        (0b00, 0b01000): TrainAction.AUX1_OFF,
        (0b00, 0b01001): TrainAction.AUX1_OPTION_1,
        (0b00, 0b01010): TrainAction.AUX1_OPTION_2,
        (0b00, 0b01011): TrainAction.AUX1_ON,
        (0b00, 0b01100): TrainAction.AUX2_OFF,
        (0b00, 0b01101): TrainAction.AUX2_OPTION_1,
        (0b00, 0b01110): TrainAction.AUX2_OPTION_2,
        (0b00, 0b01111): TrainAction.AUX2_ON,
        (0b00, 0b11100): TrainAction.BLOW_HORN_1,
        (0b00, 0b11101): TrainAction.RING_BELL,
        (0b00, 0b11110): TrainAction.LETOFF,
        (0b00, 0b11111): TrainAction.BLOW_HORN_2,
        (0b01, 0b01000): TrainAction.MOMENTUM_LOW,
        (0b01, 0b01001): TrainAction.MOMENTUM_MEDIUM,
        (0b01, 0b01010): TrainAction.MOMENTUM_HIGH,
    }

    @classmethod
    def decode(cls, packet):
        """
        Decode a 3-byte TMCC command packet into a structured object.

        Validates the packet header, reconstructs the 16-bit word,
        determines the command type, and returns a DecodedCommand
        object with all fields populated.

        Args:
            packet (bytes): A 3-byte TMCC command packet

        Returns:
            DecodedCommand: Object containing decoded command fields

        Raises:
            ValueError: If packet is not exactly 3 bytes
            ValueError: If first byte is not the TMCC header (0xFE)
        """
        if len(packet) != 3:
            raise ValueError("TMCC packet must be exactly 3 bytes")
        if packet[0] != 0xFE:
            raise ValueError(f"Invalid TMCC header byte: {hex(packet[0])}")

        # Reconstruct 16-bit word from bytes 2 and 3
        word = (packet[1] << 8) | packet[2]

        # Extract bits 15-14 to determine command type
        cmd_type_bits = (word >> 14) & 0b11

        if cmd_type_bits == cls.ENGINE_BITS:
            return cls._decode_engine(word)
        elif cmd_type_bits == cls.ACCESSORY_BITS:
            return cls._decode_accessory(word)
        elif cmd_type_bits == cls.SWITCH_BITS:
            return cls._decode_switch_or_route(word)
        elif cmd_type_bits == cls.TRAIN_BITS:
            return cls._decode_train(word)
        else:
            raise ValueError(f"Unknown command type bits: {bin(cmd_type_bits)}")

    @classmethod
    def _decode_engine(cls, word):
        """
        Decode a 16-bit engine command word.

        Engine command bit format:
            Bits 15-14: 00 (engine identifier)
            Bits 13-7:  AAAAAAA (7-bit address)
            Bits 6-5:   CC (command field)
            Bits 4-0:   DDDDD (data field)

        Args:
            word (int): 16-bit command word

        Returns:
            DecodedCommand: Decoded engine command object
        """
        address = (word >> 7) & 0x7F
        command_field = (word >> 5) & 0x03
        data_field = word & 0x1F

        # Handle speed commands separately as they carry dynamic values
        if command_field == 0b10:
            action = EngineAction.RELATIVE_SPEED
            speed_value = data_field - 5
        elif command_field == 0b11:
            action = EngineAction.ABSOLUTE_SPEED
            speed_value = data_field
        else:
            action = cls.ENGINE_ACTION_MAP.get(
                (command_field, data_field), EngineAction.UNKNOWN
            )
            speed_value = None

        description = cls._build_description(
            CommandType.ENGINE, address, action, speed_value
        )

        return DecodedCommand(
            command_type=CommandType.ENGINE,
            address=address,
            command_field=command_field,
            data_field=data_field,
            action=action,
            speed_value=speed_value,
            description=description,
            raw_word=word
        )

    @classmethod
    def _decode_switch_or_route(cls, word):
        """
        Decode a 16-bit switch or route command word.

        Distinguishes between switch and route based on bits 13-12.

        Switch command bit format:
            Bits 15-14: 01
            Bits 13-12: 00 (switch identifier)
            Bits 11-5:  AAAAAAA (7-bit address)
            Bits 4-0:   DDDDD (data field)

        Route command bit format:
            Bits 15-14: 01
            Bits 13-12: 10 (route identifier)
            Bits 11-5:  AAAAAAA (7-bit address)
            Bits 4-0:   DDDDD (data field)

        Args:
            word (int): 16-bit command word

        Returns:
            DecodedCommand: Decoded switch or route command object
        """
        sub_type = (word >> 12) & 0b11
        address = (word >> 5) & 0x7F
        data_field = word & 0x1F
        command_field = (word >> 3) & 0x03

        if sub_type == 0b10:
            command_type = CommandType.ROUTE
            action = RouteAction.ROUTE_THROW if (data_field & 0b11111) == 0b11111 \
                else RouteAction.ROUTE_CLEAR
        else:
            command_type = CommandType.SWITCH
            action = cls.SWITCH_ACTION_MAP.get(data_field, SwitchAction.UNKNOWN)

        description = cls._build_description(command_type, address, action)

        return DecodedCommand(
            command_type=command_type,
            address=address,
            command_field=command_field,
            data_field=data_field,
            action=action,
            speed_value=None,
            description=description,
            raw_word=word
        )

    @classmethod
    def _decode_accessory(cls, word):
        """
        Decode a 16-bit accessory command word.

        Accessory command bit format:
            Bits 15-14: 10
            Bits 13-7:  AAAAAAA (7-bit address)
            Bits 6-5:   CC (command field)
            Bits 4-0:   DDDDD (data field)

        Args:
            word (int): 16-bit command word

        Returns:
            DecodedCommand: Decoded accessory command object
        """
        address = (word >> 7) & 0x7F
        command_field = (word >> 5) & 0x03
        data_field = word & 0x1F

        action = cls.ACCESSORY_ACTION_MAP.get(data_field, AccessoryAction.UNKNOWN)
        description = cls._build_description(CommandType.ACCESSORY, address, action)

        return DecodedCommand(
            command_type=CommandType.ACCESSORY,
            address=address,
            command_field=command_field,
            data_field=data_field,
            action=action,
            speed_value=None,
            description=description,
            raw_word=word
        )

    @classmethod
    def _decode_train(cls, word):
        """
        Decode a 16-bit train (lash-up) command word.

        Train command bit format:
            Bits 15-14: 11
            Bits 13-12: 00
            Bits 11-7:  AAAAA (5-bit address, train ID)
            Bits 6-5:   CC (command field)
            Bits 4-0:   DDDDD (data field)

        Args:
            word (int): 16-bit command word

        Returns:
            DecodedCommand: Decoded train command object
        """
        address = (word >> 7) & 0x1F
        command_field = (word >> 5) & 0x03
        data_field = word & 0x1F

        # Handle speed commands separately as they carry dynamic values
        if command_field == 0b10:
            action = TrainAction.RELATIVE_SPEED
            speed_value = data_field - 5
        elif command_field == 0b11:
            action = TrainAction.ABSOLUTE_SPEED
            speed_value = data_field
        else:
            action = cls.TRAIN_ACTION_MAP.get(
                (command_field, data_field), TrainAction.UNKNOWN
            )
            speed_value = None

        description = cls._build_description(
            CommandType.TRAIN, address, action, speed_value
        )

        return DecodedCommand(
            command_type=CommandType.TRAIN,
            address=address,
            command_field=command_field,
            data_field=data_field,
            action=action,
            speed_value=speed_value,
            description=description,
            raw_word=word
        )

    @classmethod
    def _build_description(cls, command_type, address, action, speed_value=None):
        """
        Build a human-readable description string for a decoded command.

        For speed commands, appends the speed value to the description.
        For all other commands, uses the action enum's value string.

        Args:
            command_type (CommandType): Type of TMCC command
            address (int): ID number of the target device
            action (Enum): Action enum value
            speed_value (int, optional): Speed value for speed commands

        Returns:
            str: Human-readable command description
        """
        if speed_value is not None:
            if action in (EngineAction.RELATIVE_SPEED, TrainAction.RELATIVE_SPEED):
                speed_str = f"{'+' if speed_value >= 0 else ''}{speed_value}"
                return f"{command_type.value} {address}: {action.value} {speed_str}"
            else:
                return f"{command_type.value} {address}: {action.value} {speed_value}"
        return f"{command_type.value} {address}: {action.value}"


class DecodedCommand:
    """
    Represents a decoded TMCC command packet.

    Contains all fields extracted from the 3-byte TMCC packet
    including the command type, address, command field, data
    field, action enum, speed value, description, and the
    original raw word.
    """

    def __init__(self, command_type, address, command_field,
                 data_field, action, speed_value, description, raw_word):
        """
        Initialize a DecodedCommand object.

        Args:
            command_type (CommandType): Type of command enum value
            address (int): ID number of the target device
            command_field (int): 2-bit command field value
            data_field (int): 5-bit data field value
            action (Enum): Action enum value
            speed_value (int or None): Speed value for speed commands, else None
            description (str): Full human-readable command description
            raw_word (int): Original 16-bit command word
        """
        self.command_type = command_type
        self.address = address
        self.command_field = command_field
        self.data_field = data_field
        self.action = action
        self.speed_value = speed_value
        self.description = description
        self.raw_word = raw_word

    def __str__(self):
        """
        Return human-readable string representation of the command.

        Returns:
            str: Human-readable command description
        """
        return self.description

    def __repr__(self):
        """
        Return detailed string representation of the command for debugging.

        Returns:
            str: Detailed command representation with all fields
        """
        return (
            f"DecodedCommand("
            f"type={self.command_type.value}, "
            f"address={self.address}, "
            f"command_field={bin(self.command_field)}, "
            f"data_field={bin(self.data_field)}, "
            f"action={self.action}, "
            f"speed_value={self.speed_value}, "
            f"raw_word={bin(self.raw_word)})"
        )