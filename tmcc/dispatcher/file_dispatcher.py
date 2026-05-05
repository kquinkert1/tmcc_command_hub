import json
import time
import logging
import argparse
from datetime import datetime

from dispatcher import Dispatcher
from tmcc.adaptors.file_adaptor import FileAdaptor
from tmcc.factory.tmcc_command_factory import TMCCCommandFactory
from tmcc.tmcc_subscriptions import TMCCSubscriptions

log = logging.getLogger(__name__)


class FileDispatcher(Dispatcher):

    def __init__(self, filename: str = None, verbose: bool = False, metered: float = None):
        super().__init__()
        self._filename = filename
        self._verbose = verbose
        self._metered = metered
        self._adaptor = self.create_adaptor()
        self._subscriptions = TMCCSubscriptions()
        self._subscriptions.connect()

    def create_adaptor(self):
        return FileAdaptor(filename=self._filename)

    def read(self) -> bytes:
        return self._adaptor.read()

    def send(self, packet: bytes):
        self._adaptor.send(packet)

    def publish(self, command):
        topic = f"tmcc/{command.command_type.value.lower()}/{command.address}"
        payload = {
            'command_type': command.command_type.value,
            'address': command.address,
            'command_field': command.command_field,
            'data_field': command.data_field,
            'action': command.action.value,
            'speed_value': command.speed_value,
            'description': command.description,
            'raw_word': command.raw_word
        }
        self._subscriptions.publish(topic, payload)
        if self._verbose:
            ts = datetime.now().strftime('%H:%M:%S.%f')[:11]
            log.info(f"{ts}  {topic}  {json.dumps(payload)}")

    def run(self):
        with self._adaptor:
            print(f"Reading from: {self._adaptor._filename}")
            while True:
                packet = self.read()
                if packet is None:
                    break
                command = TMCCCommandFactory.decode(packet)
                self.publish(command)
                if self._metered:
                    time.sleep(self._metered)
        self._subscriptions.disconnect()


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    parser = argparse.ArgumentParser(description='Dispatch TMCC packets from a file.')
    parser.add_argument('-f', '--filename', help='File to read from')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')
    parser.add_argument('--metered', type=float, metavar='seconds', help='Delay between commands')
    args = parser.parse_args()

    dispatcher = FileDispatcher(filename=args.filename, verbose=args.verbose, metered=args.metered)
    dispatcher.run()
