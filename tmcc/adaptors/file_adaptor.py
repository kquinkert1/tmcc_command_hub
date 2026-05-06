import configparser
import logging
import os
import argparse
from tmcc.adaptors.adaptor import Adaptor

log = logging.getLogger(__name__)


class FileAdaptor(Adaptor):
    """
    Reads TMCC packets from a file, one hex entry per line.
    send() is a no-op.
    """

    CONFIG_FILE = os.path.join(os.path.dirname(__file__), '..', '..', 'tmcc.ini')
    CONFIG_SECTION = 'FileAdaptor'
    CONFIG_KEY = 'filename'

    def __init__(self, filename: str = None):
        self._filename = filename or self._load_filename()
        self._file = None

    @property
    def filename(self) -> str:
        return self._filename

    def _load_filename(self) -> str:
        config = configparser.ConfigParser()
        abs_config = os.path.abspath(self.CONFIG_FILE)
        config.read(abs_config)
        filename = config[self.CONFIG_SECTION][self.CONFIG_KEY]
        abs_filename = os.path.abspath(filename)
        log.debug(f"Config file: {abs_config}, section: [{self.CONFIG_SECTION}], key: {self.CONFIG_KEY} = {abs_filename}")
        return filename

    def start(self):
        self._file = open(self._filename)

    def stop(self):
        if self._file:
            self._file.close()
            self._file = None

    def read(self) -> tuple:
        """Read next valid line and return (packet, comment) tuple."""
        for line in self._file:
            parts = line.split('#', 1)
            comment = parts[1].strip() if len(parts) > 1 else ''
            line = parts[0].strip()
            if not line:
                continue
            tokens = line.split()
            try:
                if len(tokens) == 2:
                    b1 = int(tokens[0], 16)
                    b2 = int(tokens[1], 16)
                elif len(tokens) == 1:
                    cleaned = tokens[0].replace('0x', '').replace(':', '')
                    b1 = int(cleaned[0:2], 16)
                    b2 = int(cleaned[2:4], 16)
                else:
                    continue
                log.debug(comment)
                return bytes([0xFE, b1, b2]), comment
            except ValueError:
                continue
        return None, ''  # EOF

    def send(self, packet: bytes):
        """No-op for file-based adaptor."""
        pass


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    parser = argparse.ArgumentParser(description='Read TMCC packets from a file.')
    parser.add_argument('-f', '--filename', help='File to read from')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')
    args = parser.parse_args()

    adaptor = FileAdaptor(filename=args.filename)
    print(f"Reading from: {os.path.abspath(adaptor.filename)}")

    with adaptor:
        while True:
            packet, comment = adaptor.read()
            if packet is None:
                break
            if args.verbose:
                print(f"  {packet.hex()}  {comment}")
