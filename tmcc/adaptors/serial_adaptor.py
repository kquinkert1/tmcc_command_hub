import configparser
import logging
import os
import serial
from tmcc.adaptors.adaptor import Adaptor

log = logging.getLogger(__name__)


class SerialAdaptor(Adaptor):
    """
    Reads TMCC packets from a serial port (Command Base).
    """

    HEADER = 0xFE
    BAUD_RATE = 9600
    PACKET_SIZE = 3

    CONFIG_FILE = os.path.join(os.path.dirname(__file__), '..', '..', 'tmcc.ini')
    CONFIG_SECTION = 'SerialAdaptor'
    CONFIG_KEY = 'port'

    def __init__(self, port: str = None):
        self._port_name = port or self._load_port()
        self._port = None

    @property
    def port(self) -> str:
        return self._port_name

    def _load_port(self) -> str:
        config = configparser.ConfigParser()
        abs_config = os.path.abspath(self.CONFIG_FILE)
        config.read(abs_config)
        port = config[self.CONFIG_SECTION][self.CONFIG_KEY]
        log.debug(f"Config file: {abs_config}, section: [{self.CONFIG_SECTION}], key: {self.CONFIG_KEY} = {port}")
        return port

    def start(self):
        self._port = serial.Serial(
            port=self._port_name,
            baudrate=self.BAUD_RATE,
            stopbits=serial.STOPBITS_ONE,
            parity=serial.PARITY_NONE,
            bytesize=serial.EIGHTBITS,
            timeout=1
        )
        log.debug(f"Opened serial port: {self._port_name}")

    def stop(self):
        if self._port and self._port.is_open:
            self._port.close()
            log.debug(f"Closed serial port: {self._port_name}")

    def read(self) -> tuple:
        """Blocking read of next 3-byte TMCC packet."""
        while self._port and self._port.is_open:
            header = self._port.read(1)
            if header and header[0] == self.HEADER:
                rest = self._port.read(self.PACKET_SIZE - 1)
                if len(rest) == self.PACKET_SIZE - 1:
                    return header + rest, ''
        return None, ''

    def send(self, packet: bytes):
        """Send a 3-byte TMCC packet to the Command Base."""
        if len(packet) != self.PACKET_SIZE:
            raise ValueError(f"TMCC packet must be exactly {self.PACKET_SIZE} bytes")
        self._port.write(packet)

