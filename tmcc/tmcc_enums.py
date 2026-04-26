from enum import Enum


class CommandType(Enum):
    """
    Identifies the type of TMCC command decoded from bits 15-14
    of the 16-bit command word.
    """
    ENGINE = "Engine"
    TRAIN = "Train"
    SWITCH = "Switch"
    ROUTE = "Route"
    ACCESSORY = "Accessory"


class EngineAction(Enum):
    """
    All possible action commands for a TMCC engine.
    Values correspond to human-readable descriptions.
    """
    # Direction commands
    FORWARD = "Forward"
    REVERSE = "Reverse"
    TOGGLE_DIR = "Toggle Direction"

    # Speed commands
    BOOST = "Boost"
    BRAKE = "Brake"

    # Coupler commands
    OPEN_FRONT_COUPLER = "Open Front Coupler"
    OPEN_REAR_COUPLER = "Open Rear Coupler"

    # Sound commands
    BLOW_HORN_1 = "Blow Horn 1"
    BLOW_HORN_2 = "Blow Horn 2"
    RING_BELL = "Ring Bell"
    LETOFF = "Letoff Sound"

    # AUX1 commands
    AUX1_OFF = "AUX1 Off"
    AUX1_OPTION_1 = "AUX1 Option 1"
    AUX1_OPTION_2 = "AUX1 Option 2"
    AUX1_ON = "AUX1 On"

    # AUX2 commands
    AUX2_OFF = "AUX2 Off"
    AUX2_OPTION_1 = "AUX2 Option 1"
    AUX2_OPTION_2 = "AUX2 Option 2"
    AUX2_ON = "AUX2 On"

    # Momentum commands
    MOMENTUM_LOW = "Momentum Low"
    MOMENTUM_MEDIUM = "Momentum Medium"
    MOMENTUM_HIGH = "Momentum High"

    # Address command
    SET_ADDRESS = "Set Address"

    # Numeric commands
    NUMERIC_0 = "Numeric 0"
    NUMERIC_1 = "Numeric 1"
    NUMERIC_2 = "Numeric 2"
    NUMERIC_3 = "Numeric 3"
    NUMERIC_4 = "Numeric 4"
    NUMERIC_5 = "Numeric 5"
    NUMERIC_6 = "Numeric 6"
    NUMERIC_7 = "Numeric 7"
    NUMERIC_8 = "Numeric 8"
    NUMERIC_9 = "Numeric 9"

    # Speed commands (dynamic values handled separately)
    ABSOLUTE_SPEED = "Absolute Speed"
    RELATIVE_SPEED = "Relative Speed"

    # Unknown
    UNKNOWN = "Unknown"


class SwitchAction(Enum):
    """
    All possible action commands for a TMCC switch.
    """
    THROW_THROUGH = "Throw Through"
    THROW_OUT = "Throw Out"
    SET_ADDRESS = "Set Address"
    UNKNOWN = "Unknown"


class RouteAction(Enum):
    """
    All possible action commands for a TMCC route.
    """
    ROUTE_THROW = "Route Throw"
    ROUTE_CLEAR = "Route Clear"
    UNKNOWN = "Unknown"


class AccessoryAction(Enum):
    """
    All possible action commands for a TMCC accessory.
    """
    # AUX1 commands
    AUX1_OFF = "AUX1 Off"
    AUX1_OPTION_1 = "AUX1 Option 1"
    AUX1_OPTION_2 = "AUX1 Option 2"
    AUX1_ON = "AUX1 On"

    # AUX2 commands
    AUX2_OFF = "AUX2 Off"
    AUX2_OPTION_1 = "AUX2 Option 1"
    AUX2_OPTION_2 = "AUX2 Option 2"
    AUX2_ON = "AUX2 On"

    # Extended commands
    ALL_OFF = "All Off"
    ALL_ON = "All On"
    SET_ADDRESS = "Set Address"

    # Unknown
    UNKNOWN = "Unknown"


class TrainAction(Enum):
    """
    All possible action commands for a TMCC train (lash-up).
    Train commands mirror engine commands.
    """
    # Direction commands
    FORWARD = "Forward"
    REVERSE = "Reverse"
    TOGGLE_DIR = "Toggle Direction"

    # Speed commands
    BOOST = "Boost"
    BRAKE = "Brake"

    # Coupler commands
    OPEN_FRONT_COUPLER = "Open Front Coupler"
    OPEN_REAR_COUPLER = "Open Rear Coupler"

    # Sound commands
    BLOW_HORN_1 = "Blow Horn 1"
    BLOW_HORN_2 = "Blow Horn 2"
    RING_BELL = "Ring Bell"
    LETOFF = "Letoff Sound"

    # AUX1 commands
    AUX1_OFF = "AUX1 Off"
    AUX1_OPTION_1 = "AUX1 Option 1"
    AUX1_OPTION_2 = "AUX1 Option 2"
    AUX1_ON = "AUX1 On"

    # AUX2 commands
    AUX2_OFF = "AUX2 Off"
    AUX2_OPTION_1 = "AUX2 Option 1"
    AUX2_OPTION_2 = "AUX2 Option 2"
    AUX2_ON = "AUX2 On"

    # Momentum commands
    MOMENTUM_LOW = "Momentum Low"
    MOMENTUM_MEDIUM = "Momentum Medium"
    MOMENTUM_HIGH = "Momentum High"

    # Speed commands (dynamic values handled separately)
    ABSOLUTE_SPEED = "Absolute Speed"
    RELATIVE_SPEED = "Relative Speed"

    # Unknown
    UNKNOWN = "Unknown"
