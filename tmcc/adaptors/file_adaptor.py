import logging
import os

from adaptors.adaptor import Adaptor

log = logging.getLogger(__name__)


class FileAdaptor(Adaptor):
    """
    Reads TMCC packets from a file, one hex entry per line.
    send() is a no-op.
    """

    CONFIG_FILE = '../../tmcc.ini'
    CONFIG_SECTION = 'FileAdaptor'
    CONFIG_KEY = 'filename'

    def __init__(self, filename: str = None):
        self._filename = filename or self._load_filename()
        self._file = None
    def _load_filename(self) -> str:
        import configparser
        config = configparser.ConfigParser()
        abs_config = os.path.abspath(self.CONFIG_FILE)

        config.read(self.CONFIG_FILE)
        log.debug( f"Config file: {self.CONFIG_FILE}, section: [{self.CONFIG_SECTION}], key: {self.CONFIG_KEY}")
        filename = config[self.CONFIG_SECTION][self.CONFIG_KEY]
        abs_file = os.path.abspath(filename)
        return filename
    def start(self):
        self._file = open(self._filename)

    def stop(self):
        if self._file:
            self._file.close()
            self._file = None

    def read(self) -> bytes:
        """Read next valid line and return as a 3-byte packet."""
        for line in self._file:
            line = line.strip()
            if not line or line.startswith('#'):
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
                return bytes([0xFE, b1, b2])
            except ValueError:
                continue
        return None  # EOF

    def send(self, packet: bytes):
        """No-op for file-based adaptor."""
        pass


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Read TMCC packets from a file.')
    parser.add_argument('-f', '--filename', help='File to read from')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')
    args = parser.parse_args()

    adaptor = FileAdaptor(filename=args.filename)
    print(f"Reading from: {adaptor._filename}")

    with adaptor:
        while True:
            packet = adaptor.read()
            if packet is None:
                break
            if args.verbose:
                print(f"  {packet.hex()}")