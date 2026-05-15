import json
import os
import time
import logging
import argparse
import configparser
from datetime import datetime

from dispatcher import Dispatcher
from tmcc.adaptors.serial_adaptor import SerialAdaptor
from tmcc.factory.tmcc_command_factory import TMCCCommandFactory
from tmcc.tmcc_subscriptions import TMCCSubscriptions
from tmcc.models.engine import Engine
from tmcc.tmcc_enums import CommandType
from tmcc.commands.engine_command import EngineCommand

log = logging.getLogger(__name__)

PUBLISH_INTERVAL = 5  # seconds

CONFIG_FILE = os.path.join(os.path.dirname(__file__), '..', '..', 'tmcc.ini')
CONFIG_SECTION = 'SerialDispatcher'
CONFIG_KEY = 'log_filename'


class SerialDispatcher(Dispatcher):

    def __init__(self, port: str = None, verbose: bool = False):
        super().__init__()
        self._port = port
        self._verbose = verbose
        self._log_filename = self._load_log_filename()
        self._log_file = None
        self._adaptor = self.create_adaptor()
        self._subscriptions = TMCCSubscriptions()
        self._subscriptions.connect()
        self._engines = {}
        self._dirty = set()

        # Subscribe to send commands
        self._subscriptions.subscribe('tmcc_send/engine/#', self._on_send_command)

    def _load_log_filename(self) -> str:
        config = configparser.RawConfigParser()
        abs_config = os.path.abspath(CONFIG_FILE)
        config.read(abs_config)
        filename = config[CONFIG_SECTION][CONFIG_KEY]
        if '{timestamp}' in filename:
            ts = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
            filename = filename.replace('{timestamp}', ts)
        abs_filename = os.path.abspath(filename)
        log.debug(f"Log file: {abs_filename}")
        return filename

    def create_adaptor(self):
        return SerialAdaptor(port=self._port)

    def read(self) -> tuple:
        return self._adaptor.read()

    def send(self, packet: bytes, priority: bool = False):
        self._adaptor.send(packet, priority=priority)

    def _initialize_engines(self):
        config = configparser.RawConfigParser()
        config.read(os.path.abspath(CONFIG_FILE))
        if 'EngineMaxSpeeds' not in config:
            log.warning("No [EngineMaxSpeeds] section found in ini")
            return
        for engine_id_str in config['EngineMaxSpeeds']:
            engine_id = int(engine_id_str)
            log.info(f"Initializing engine {engine_id}: direction=FORWARD, speed=0")
            fwd_packet = EngineCommand.build_command(engine_id, EngineCommand.FORWARD)
            self.send(fwd_packet, priority=True)
            log.debug(f"Engine {engine_id}: sent FORWARD_DIRECTION")
            time.sleep(0.25)
            stop_packet = EngineCommand.build_command(engine_id, EngineCommand.ABSOLUTE_SPEED, 0)
            self.send(stop_packet, priority=True)
            log.debug(f"Engine {engine_id}: sent ABSOLUTE_SPEED=0")
            time.sleep(0.25)

    def _on_send_command(self, client, userdata, message):
        try:
            payload = json.loads(message.payload)
            action = payload.get('action')
            address = payload.get('address')
            priority = payload.get('priority', False)

            if action == 'ABSOLUTE_SPEED':
                speed = min(int(payload.get('speed', 0)), EngineCommand.MAX_ABSOLUTE_SPEED)
                packet = EngineCommand.build_command(address, EngineCommand.ABSOLUTE_SPEED, speed)
            elif action == 'RELATIVE_SPEED':
                delta = payload.get('delta', 0)
                packet = EngineCommand.build_command(address, EngineCommand.RELATIVE_SPEED, delta + 5)
            elif hasattr(EngineCommand, action):
                data_field = getattr(EngineCommand, action)
                packet = EngineCommand.build_command(address, EngineCommand.ACTION, data_field)
            else:
                log.warning(f"Unknown action: {action}")
                return

            log.info(f"Send command: {message.topic}  {payload}")
            self.send(packet, priority=priority)

            # Update engine state
            engine = self._get_or_create_engine(address)
            engine.update(packet)
            self._dirty.add(address)

        except Exception as e:
            log.error(f"Error processing send command: {e}")

    def _get_or_create_engine(self, address: int) -> Engine:
        if address not in self._engines:
            self._engines[address] = Engine(address)
        return self._engines[address]

    def _log_packet(self, packet: bytes, command):
        """Log packet in tmcc.log format: 0xB1 0xB2  # description"""
        if self._log_file:
            b1 = packet[1]
            b2 = packet[2]
            self._log_file.write(f" 0x{b1:x} 0x{b2:x}  # {command.description}\n")
            self._log_file.flush()

    def publish(self, engine: Engine):
        topic = f"tmcc/engine/{engine.id}"
        payload = {
            'id': engine.id,
            'speed': engine.speed,
            'max_speed': engine.max_speed,
            'direction': engine.direction,
            'bell': engine.bell,
            'last_command': engine.last_command or '',
            'line_comment': engine.line_comment,
            'command_timestamp': engine.command_timestamp.strftime('%H:%M:%S.%f')[:11],
            'message_timestamp': datetime.now().strftime('%H:%M:%S.%f')[:11]
        }
        self._subscriptions.publish(topic, payload)
        if self._verbose:
            ts = datetime.now().strftime('%H:%M:%S.%f')[:11]
            log.info(f"{ts}  {topic}  {json.dumps(payload)}")

    def run(self):
        last_publish = time.time()
        os.makedirs(os.path.dirname(os.path.abspath(self._log_filename)), exist_ok=True)
        print(f"Listening on serial port: {self._adaptor.port}")
        print(f"Logging to: {os.path.abspath(self._log_filename)}")
        try:
            with open(self._log_filename, 'a') as self._log_file:
                with self._adaptor:
                    self._initialize_engines()
                    while True:
                        packet, comment = self.read()
                        now = time.time()

                        if packet is not None:
                            command = TMCCCommandFactory.decode(packet)
                            self._log_packet(packet, command)
                            if command.command_type == CommandType.ENGINE:
                                engine = self._get_or_create_engine(command.address)
                                engine.update(packet, comment)
                                self._dirty.add(command.address)

                        # Publish dirty engines immediately
                        for address in list(self._dirty):
                            self.publish(self._engines[address])
                        self._dirty.clear()

                        # Publish all engines every 5 seconds
                        if now - last_publish >= PUBLISH_INTERVAL:
                            for engine in self._engines.values():
                                log.debug(f"publish interval: {engine}")
                                self.publish(engine)
                            last_publish = now

        except KeyboardInterrupt:
            print("\nStopping...")
        finally:
            self._subscriptions.disconnect()


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    parser = argparse.ArgumentParser(description='Dispatch TMCC packets from serial port.')
    parser.add_argument('-p', '--port', help='Serial port (e.g. /dev/ttyS0)')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')
    parser.add_argument('--list-ports', action='store_true', help='List available serial ports and exit')
    args = parser.parse_args()

    if args.list_ports:
        import serial.tools.list_ports
        ports = serial.tools.list_ports.comports()
        if ports:
            for p in ports:
                print(f"{p.device}  {p.description}")
        else:
            print("No serial ports found.")
        exit(0)

    dispatcher = SerialDispatcher(port=args.port, verbose=args.verbose)
    dispatcher.run()
