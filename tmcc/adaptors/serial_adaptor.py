import configparser
import logging
import os
import serial
import threading
import time
from queue import Queue, Empty
from tmcc.adaptors.adaptor import Adaptor
from tmcc.commands.engine_command import EngineCommand

log = logging.getLogger(__name__)

YOP_INTERVAL = 3       # seconds
NORMAL_QUEUE_DELAY = 0.25  # seconds since last receive before sending normal


class SerialAdaptor(Adaptor):
    """
    Reads TMCC packets from a serial port (Command Base).
    Sends packets via a priority/normal queue send thread.
    YOP keepalive sent every 3 seconds via priority queue.
    Normal queue only sends if no packet received in last 0.25 seconds.
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
        self._running = False
        self._last_send = 0
        self._last_receive = 0
        self._priority_queue = Queue()
        self._normal_queue = Queue()
        self._send_thread = None
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
        self._last_receive = time.time()

        self._send_thread = threading.Thread(target=self._send_loop, daemon=True)
        self._send_thread.start()

        self._yop_thread = threading.Thread(target=self._yop_loop, daemon=True)
        self._yop_thread.start()

    def stop(self):
        self._running = False
        if self._send_thread:
            self._send_thread.join(timeout=2)
        if self._yop_thread:
            self._yop_thread.join(timeout=2)
        if self._port and self._port.is_open:
            self._port.close()
            log.debug(f"Closed serial port: {self._port_name}")

    def _send_loop(self):
        """
        Send thread:
        - Priority queue: always drain first
        - Normal queue: only send if no packet received in last 0.25 seconds
        """
        while self._running:
            packet = None

            # Drain priority queue first
            try:
                packet = self._priority_queue.get_nowait()
            except Empty:
                # Normal queue only if port has been quiet for 0.25 seconds
                if time.time() - self._last_receive >= NORMAL_QUEUE_DELAY:
                    try:
                        packet = self._normal_queue.get_nowait()
                    except Empty:
                        pass

            if packet:
                try:
                    self._port.write(packet)
                    self._last_send = time.time()
                except Exception as e:
                    log.warning(f"Send failed: {e}")
            else:
                time.sleep(0.01)

    def _yop_loop(self):
        """Send YOP keepalive every 3 seconds since last send."""
        while self._running:
            time.sleep(0.5)
            if time.time() - self._last_send >= YOP_INTERVAL:
                self._priority_queue.put(EngineCommand.yop())

    def read(self) -> tuple:
        """Blocking read of next 3-byte TMCC packet, returns None on timeout."""
        while self._port and self._port.is_open:
            header = self._port.read(1)
            if not header:
                return None, ''  # timeout - let dispatcher check interval
            if header[0] == self.HEADER:
                rest = self._port.read(self.PACKET_SIZE - 1)
                if len(rest) == self.PACKET_SIZE - 1:
                    self._last_receive = time.time()
                    return header + rest, ''
        return None, ''

    def send(self, packet: bytes, priority: bool = False):
        """Queue a 3-byte TMCC packet for sending."""
        if len(packet) != self.PACKET_SIZE:
            raise ValueError(f"TMCC packet must be exactly {self.PACKET_SIZE} bytes")
        if priority:
            self._priority_queue.put(packet)
        else:
            self._normal_queue.put(packet)