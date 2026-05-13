import configparser
import logging
import os
import serial
import threading
import time
from tmcc.adaptors.adaptor import Adaptor
from tmcc.commands.engine_command import EngineCommand

log = logging.getLogger(__name__)

YOP_INTERVAL = 3  # seconds


class SerialAdaptor(Adaptor):
    """
    Reads TMCC packets from a serial port (Command Base).
    Sends YOP keepalive every 3 seconds since last send.
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
        self._last_send = 0
        self._running = False
        self._yop_thread = None

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
        self._running = True
        self._last_send = time.time()
        self._yop_thread = threading.Thread(target=self._yop_loop, daemon=True)
        self._yop_thread.start()

    def stop(self):
        self._running = False
        if self._yop_thread:
            self._yop_thread.join(timeout=2)
        if self._port and self._port.is_open:
            self._port.close()
            log.debug(f"Closed serial port: {self._port_name}")

    def _yop_loop(self):
        """Send YOP keepalive every 3 seconds since last send."""
        while self._running:
            time.sleep(0.5)
            if time.time() - self._last_send >= YOP_INTERVAL:
                self._send_yop()

    def _send_yop(self):
        """Send YOP keepalive packet."""
        try:
            packet = EngineCommand.yop()
            self._port.write(packet)
            self._last_send = time.time()
        except Exception as e:
            log.warning(f"YOP send failed: {e}")

    def read(self) -> tuple:
        """Blocking read of next 3-byte TMCC packet."""
        while self._port and self._port.is_open:
            header = self._port.read(1)
            if not header:
                return None, ''  # timeout - let dispatcher check interval
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
        self._last_send = time.time()