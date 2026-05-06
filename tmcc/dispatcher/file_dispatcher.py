import json
import os
import time
import logging
import argparse
from datetime import datetime

from dispatcher import Dispatcher
from tmcc.adaptors.file_adaptor import FileAdaptor
from tmcc.factory.tmcc_command_factory import TMCCCommandFactory
from tmcc.tmcc_subscriptions import TMCCSubscriptions
from tmcc.models.engine import Engine
from tmcc.tmcc_enums import CommandType

log = logging.getLogger(__name__)

PUBLISH_INTERVAL = 5  # seconds


class FileDispatcher(Dispatcher):

    def __init__(self, filename: str = None, verbose: bool = False, metered: int = None,
                 metered_delay: float = 1.0, delay_to_close: float = 0):
        super().__init__()
        self._filename = filename
        self._verbose = verbose
        self._metered = metered
        self._metered_delay = metered_delay
        self._delay_to_close = delay_to_close
        self._adaptor = self.create_adaptor()
        self._subscriptions = TMCCSubscriptions()
        self._subscriptions.connect()
        self._engines = {}  # address -> Engine
        self._dirty = set()  # addresses needing publish

    def create_adaptor(self):
        return FileAdaptor(filename=self._filename)

    def read(self) -> tuple:
        return self._adaptor.read()

    def send(self, packet: bytes):
        self._adaptor.send(packet)

    def _get_or_create_engine(self, address: int) -> Engine:
        if address not in self._engines:
            self._engines[address] = Engine(address)
        return self._engines[address]

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
            'timestamp': engine.timestamp.strftime('%H:%M:%S.%f')[:11]
        }
        self._subscriptions.publish(topic, payload)
        if self._verbose:
            ts = datetime.now().strftime('%H:%M:%S.%f')[:11]
            log.info(f"{ts}  {topic}  {json.dumps(payload)}")

    def run(self):
        last_publish = time.time()
        command_count = 0
        with self._adaptor:
            print(f"Reading from: {os.path.abspath(self._adaptor.filename)}")
            while True:
                packet, comment = self.read()
                now = time.time()

                if packet is not None:
                    command = TMCCCommandFactory.decode(packet)
                    if command.command_type == CommandType.ENGINE:
                        engine = self._get_or_create_engine(command.address)
                        engine.update(packet, comment)
                        self._dirty.add(command.address)

                    command_count += 1
                    if self._metered and command_count >= self._metered:
                        for address in list(self._dirty):
                            self.publish(self._engines[address])
                        self._dirty.clear()
                        time.sleep(self._metered_delay)
                        command_count = 0

                # Publish dirty engines immediately
                for address in list(self._dirty):
                    self.publish(self._engines[address])
                self._dirty.clear()

                # Publish all engines every 5 seconds
                if now - last_publish >= PUBLISH_INTERVAL:
                    for engine in self._engines.values():
                        engine.last_command = ''
                        self.publish(engine)
                    last_publish = now

                if packet is None:
                    if self._delay_to_close == 0:
                        break
                    close_time = time.time() + self._delay_to_close
                    close_time = time.time() + self._delay_to_close
                    log.info(
                        f"EOF reached. Dispatcher will terminate at {datetime.fromtimestamp(close_time).strftime('%H:%M:%S')}")
                    while time.time() < close_time:
                        now = time.time()
                        if now - last_publish >= PUBLISH_INTERVAL:
                            for engine in self._engines.values():
                                self.publish(engine)
                            last_publish = now

                        time.sleep(0.1)
                    break

        self._subscriptions.disconnect()


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    parser = argparse.ArgumentParser(description='Dispatch TMCC packets from a file.')
    parser.add_argument('-f', '--filename', help='File to read from')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')
    parser.add_argument('--metered', type=int, metavar='commands',
                        help='Number of commands per batch, pausing between batches')
    parser.add_argument('--metered-delay', type=float, default=1.0, metavar='seconds',
                        help='Seconds to pause between metered batches (default: 1)')
    parser.add_argument('--delay-to-close', type=float, default=0, metavar='seconds',
                        help='Seconds to wait after EOF before closing (0 = do not close)')
    args = parser.parse_args()

    dispatcher = FileDispatcher(
        filename=args.filename,
        verbose=args.verbose,
        metered=args.metered,
        metered_delay=args.metered_delay,
        delay_to_close=args.delay_to_close
    )
    dispatcher.run()
