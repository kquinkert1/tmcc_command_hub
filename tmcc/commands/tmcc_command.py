import serial
from abc import ABC, abstractmethod


class TMCC_Command(ABC):
    """
    Base class for all Lionel TMCC (TrainMaster Command Control) commands.

    All TMCC commands are transmitted as 3 bytes:
        - Byte 1: Header byte (0xFE)
        - Byte 2: High byte of 16-bit command word
        - Byte 3: Low byte of 16-bit command word

    Serial communication settings per TMCC spec:
        - 9600 baud
        - 1 stop bit
        - No parity
        - 8 data bits

    Subclasses implement build_command() for their specific
    command type (Engine, Switch, Train, Accessory, Route).
    """

    HEADER = 0xFE
    BAUD_RATE = 9600
    STOP_BITS = serial.STOPBITS_ONE
    PARITY = serial.PARITY_NONE
    BYTE_SIZE = serial.EIGHTBITS

    def __init__(self, port_name):
        """
        Initialize the TMCC command base and open the serial port.

        Args:
            port_name (str): The serial port to use (e.g., '/dev/ttyS0')

        Raises:
            serial.SerialException: If the port cannot be opened
        """
        self.port = serial.Serial(
            port=port_name,
            baudrate=self.BAUD_RATE,
            stopbits=self.STOP_BITS,
            parity=self.PARITY,
            bytesize=self.BYTE_SIZE,
            timeout=1
        )

    def send(self, packet):
        """
        Send a 3-byte TMCC command packet over the serial port.

        Args:
            packet (bytes): A 3-byte TMCC command packet

        Raises:
            ValueError: If packet is not exactly 3 bytes
            serial.SerialException: If the serial write fails
        """
        if len(packet) != 3:
            raise ValueError("TMCC packet must be exactly 3 bytes")
        self.port.write(packet)

    @classmethod
    @abstractmethod
    def build_command(cls, address, command_bits, data_bits) -> bytes:
        """
        Build a 3-byte TMCC command packet from its component fields.

        Must be implemented by each subclass to apply the correct
        bit pattern for that command type (Engine, Switch, etc.).
        Returns a 3-byte packet: 0xFE + high byte + low byte.

        Args:
            address (int): The ID number of the target device
            command_bits (int): The command field bits (C)
            data_bits (int): The data field bits (D)

        Returns:
            bytes: 3-byte TMCC command packet
        """
        pass

    def close(self):
        """
        Close the serial port connection.

        Safe to call even if the port is already closed.
        """
        if self.port.is_open:
            self.port.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()