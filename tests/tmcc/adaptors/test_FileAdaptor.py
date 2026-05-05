import unittest
import configparser

from adaptors import FileAdaptor

CONFIG_FILE = './tests/test_tmcc.ini'
CONFIG_SECTION = 'test_FileAdaptor'


def get_test_filename():
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE)
    return config[CONFIG_SECTION]['filename']


class TestFileAdaptor(unittest.TestCase):

    def _make_adaptor(self, content):
        """Helper: create a FileAdaptor with mocked file content."""
        adaptor = FileAdaptor(filename='dummy')
        adaptor._file = content.splitlines(keepends=True).__iter__()
        return adaptor

    def test_read_two_byte_space_separated(self):
        adaptor = self._make_adaptor("0B 80\n")
        packet = adaptor.read()
        self.assertEqual(packet, bytes([0xFE, 0x0B, 0x80]))

    def test_read_four_char_no_space(self):
        adaptor = self._make_adaptor("0B80\n")
        packet = adaptor.read()
        self.assertEqual(packet, bytes([0xFE, 0x0B, 0x80]))

    def test_read_0x_prefix(self):
        adaptor = self._make_adaptor("0x0B 0x80\n")
        packet = adaptor.read()
        self.assertEqual(packet, bytes([0xFE, 0x0B, 0x80]))

    def test_skips_comments(self):
        adaptor = self._make_adaptor("# comment\n0B80\n")
        packet = adaptor.read()
        self.assertEqual(packet, bytes([0xFE, 0x0B, 0x80]))

    def test_skips_blank_lines(self):
        adaptor = self._make_adaptor("\n\n0B80\n")
        packet = adaptor.read()
        self.assertEqual(packet, bytes([0xFE, 0x0B, 0x80]))

    def test_eof_returns_none(self):
        adaptor = self._make_adaptor("")
        packet = adaptor.read()
        self.assertIsNone(packet)

    def test_send_is_nop(self):
        adaptor = FileAdaptor(filename='dummy')
        adaptor.send(bytes([0xFE, 0x0B, 0x80]))  # should not raise

    def test_loads_filename_from_ini(self):
        adaptor = FileAdaptor()
        self.assertEqual(adaptor._filename, get_test_filename())


if __name__ == '__main__':
    unittest.main()