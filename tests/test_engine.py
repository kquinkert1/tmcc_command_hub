import unittest
from unittest.mock import MagicMock, patch
from commands.engine_command import EngineCommand


class TestEngineCommand(unittest.TestCase):
    """
    Unit tests for the EngineCommand class.

    Uses mock serial port to avoid requiring physical
    hardware during testing.
    """

    def setUp(self):
        """
        Create an EngineCommand instance with a mocked serial port.

        Patches the serial.Serial class so no real serial port
        is required to run the tests.
        """
        with patch('serial.Serial'):
            self.engine = EngineCommand('/dev/ttyS0')
            self.engine.port = MagicMock()

    def _expected_packet(self, address, command_field, data_field):
        """
        Helper method to build expected 3-byte packet for assertion checks.

        Args:
            address (int): Engine ID number (1-99)
            command_field (int): 2-bit command field
            data_field (int): 5-bit data field

        Returns:
            bytes: Expected 3-byte TMCC command packet
        """
        return self.engine.build_command(address, command_field, data_field)

    # -------------------------
    # build_command tests
    # -------------------------

    def test_build_command_returns_bytes(self):
        """Test that build_command returns a bytes object."""
        packet = self.engine.build_command(1, 0b00, 0b00000)
        self.assertIsInstance(packet, bytes)

    def test_build_command_returns_3_bytes(self):
        """Test that build_command returns exactly 3 bytes."""
        packet = self.engine.build_command(1, 0b00, 0b00000)
        self.assertEqual(len(packet), 3)

    def test_build_command_first_byte_is_header(self):
        """Test that first byte of packet is always 0xFE."""
        packet = self.engine.build_command(1, 0b00, 0b00000)
        self.assertEqual(packet[0], 0xFE)

    def test_build_command_valid(self):
        """Test that build_command constructs correct packet for address 1."""
        packet = self.engine.build_command(1, 0b00, 0b00000)
        self.assertEqual(packet, bytes([0xFE, 0x00, 0x80]))

    def test_build_command_address_too_low(self):
        """Test that address below 1 raises ValueError."""
        with self.assertRaises(ValueError):
            self.engine.build_command(0, 0b00, 0b00000)

    def test_build_command_address_too_high(self):
        """Test that address above 99 raises ValueError."""
        with self.assertRaises(ValueError):
            self.engine.build_command(100, 0b00, 0b00000)

    def test_build_command_min_address(self):
        """Test that address of 1 is valid."""
        packet = self.engine.build_command(1, 0b00, 0b00000)
        self.assertIsNotNone(packet)

    def test_build_command_max_address(self):
        """Test that address of 99 is valid."""
        packet = self.engine.build_command(99, 0b00, 0b00000)
        self.assertIsNotNone(packet)

    # -------------------------
    # Direction command tests
    # -------------------------

    def test_forward(self):
        """Test that forward() sends correct command packet."""
        self.engine.forward(23)
        self.engine.port.write.assert_called_once_with(
            self._expected_packet(23, self.engine.ACTION, self.engine.FORWARD)
        )

    def test_reverse(self):
        """Test that reverse() sends correct command packet."""
        self.engine.reverse(23)
        self.engine.port.write.assert_called_once_with(
            self._expected_packet(23, self.engine.ACTION, self.engine.REVERSE)
        )

    def test_toggle_direction(self):
        """Test that toggle_direction() sends correct command packet."""
        self.engine.toggle_direction(23)
        self.engine.port.write.assert_called_once_with(
            self._expected_packet(23, self.engine.ACTION, self.engine.TOGGLE_DIR)
        )

    # -------------------------
    # Speed command tests
    # -------------------------

    def test_set_absolute_speed_valid(self):
        """Test that set_absolute_speed() sends correct command packet."""
        self.engine.set_absolute_speed(23, 15)
        self.engine.port.write.assert_called_once_with(
            self._expected_packet(23, self.engine.ABSOLUTE_SPEED, 15)
        )

    def test_set_absolute_speed_min(self):
        """Test that absolute speed of 0 is valid."""
        self.engine.set_absolute_speed(23, 0)
        self.assertTrue(self.engine.port.write.called)

    def test_set_absolute_speed_max(self):
        """Test that absolute speed of 31 is valid."""
        self.engine.set_absolute_speed(23, 31)
        self.assertTrue(self.engine.port.write.called)

    def test_set_absolute_speed_too_high(self):
        """Test that absolute speed above 31 raises ValueError."""
        with self.assertRaises(ValueError):
            self.engine.set_absolute_speed(23, 32)

    def test_set_absolute_speed_too_low(self):
        """Test that absolute speed below 0 raises ValueError."""
        with self.assertRaises(ValueError):
            self.engine.set_absolute_speed(23, -1)

    def test_set_relative_speed_valid(self):
        """Test that set_relative_speed() sends correct command packet."""
        self.engine.set_relative_speed(23, 3)
        self.engine.port.write.assert_called_once_with(
            self._expected_packet(23, self.engine.RELATIVE_SPEED, 3 + 5)
        )

    def test_set_relative_speed_zero(self):
        """Test that relative speed change of 0 is valid."""
        self.engine.set_relative_speed(23, 0)
        self.assertTrue(self.engine.port.write.called)

    def test_set_relative_speed_max(self):
        """Test that relative speed change of +5 is valid."""
        self.engine.set_relative_speed(23, 5)
        self.assertTrue(self.engine.port.write.called)

    def test_set_relative_speed_min(self):
        """Test that relative speed change of -5 is valid."""
        self.engine.set_relative_speed(23, -5)
        self.assertTrue(self.engine.port.write.called)

    def test_set_relative_speed_too_high(self):
        """Test that relative speed change above +5 raises ValueError."""
        with self.assertRaises(ValueError):
            self.engine.set_relative_speed(23, 6)

    def test_set_relative_speed_too_low(self):
        """Test that relative speed change below -5 raises ValueError."""
        with self.assertRaises(ValueError):
            self.engine.set_relative_speed(23, -6)

    # -------------------------
    # Sound command tests
    # -------------------------

    def test_blow_horn_1(self):
        """Test that blow_horn_1() sends correct command packet."""
        self.engine.blow_horn_1(23)
        self.engine.port.write.assert_called_once_with(
            self._expected_packet(23, self.engine.ACTION, self.engine.BLOW_HORN_1)
        )

    def test_blow_horn_2(self):
        """Test that blow_horn_2() sends correct command packet."""
        self.engine.blow_horn_2(23)
        self.engine.port.write.assert_called_once_with(
            self._expected_packet(23, self.engine.ACTION, self.engine.BLOW_HORN_2)
        )

    def test_ring_bell(self):
        """Test that ring_bell() sends correct command packet."""
        self.engine.ring_bell(23)
        self.engine.port.write.assert_called_once_with(
            self._expected_packet(23, self.engine.ACTION, self.engine.RING_BELL)
        )

    def test_letoff(self):
        """Test that letoff() sends correct command packet."""
        self.engine.letoff(23)
        self.engine.port.write.assert_called_once_with(
            self._expected_packet(23, self.engine.ACTION, self.engine.LETOFF)
        )

    # -------------------------
    # Coupler command tests
    # -------------------------

    def test_open_front_coupler(self):
        """Test that open_front_coupler() sends correct command packet."""
        self.engine.open_front_coupler(23)
        self.engine.port.write.assert_called_once_with(
            self._expected_packet(23, self.engine.ACTION, self.engine.OPEN_FRONT_COUPLER)
        )

    def test_open_rear_coupler(self):
        """Test that open_rear_coupler() sends correct command packet."""
        self.engine.open_rear_coupler(23)
        self.engine.port.write.assert_called_once_with(
            self._expected_packet(23, self.engine.ACTION, self.engine.OPEN_REAR_COUPLER)
        )

    # -------------------------
    # Boost and brake tests
    # -------------------------

    def test_boost(self):
        """Test that boost() sends correct command packet."""
        self.engine.boost(23)
        self.engine.port.write.assert_called_once_with(
            self._expected_packet(23, self.engine.ACTION, self.engine.BOOST)
        )

    def test_brake(self):
        """Test that brake() sends correct command packet."""
        self.engine.brake(23)
        self.engine.port.write.assert_called_once_with(
            self._expected_packet(23, self.engine.ACTION, self.engine.BRAKE)
        )

    # -------------------------
    # Momentum command tests
    # -------------------------

    def test_set_momentum_low(self):
        """Test that set_momentum() with 'low' sends correct command packet."""
        self.engine.set_momentum(23, 'low')
        self.engine.port.write.assert_called_once_with(
            self._expected_packet(23, self.engine.EXTENDED, self.engine.MOMENTUM_LOW)
        )

    def test_set_momentum_medium(self):
        """Test that set_momentum() with 'medium' sends correct command packet."""
        self.engine.set_momentum(23, 'medium')
        self.engine.port.write.assert_called_once_with(
            self._expected_packet(23, self.engine.EXTENDED, self.engine.MOMENTUM_MEDIUM)
        )

    def test_set_momentum_high(self):
        """Test that set_momentum() with 'high' sends correct command packet."""
        self.engine.set_momentum(23, 'high')
        self.engine.port.write.assert_called_once_with(
            self._expected_packet(23, self.engine.EXTENDED, self.engine.MOMENTUM_HIGH)
        )

    def test_set_momentum_invalid(self):
        """Test that invalid momentum level raises ValueError."""
        with self.assertRaises(ValueError):
            self.engine.set_momentum(23, 'turbo')

    # -------------------------
    # Numeric command tests
    # -------------------------

    def test_numeric_command_valid(self):
        """Test that numeric_command() sends correct command packet."""
        self.engine.numeric_command(23, 3)
        self.engine.port.write.assert_called_once_with(
            self._expected_packet(23, self.engine.ACTION, self.engine.NUMERIC_BASE | 3)
        )

    def test_numeric_command_min(self):
        """Test that numeric command of 0 is valid."""
        self.engine.numeric_command(23, 0)
        self.assertTrue(self.engine.port.write.called)

    def test_numeric_command_max(self):
        """Test that numeric command of 9 is valid."""
        self.engine.numeric_command(23, 9)
        self.assertTrue(self.engine.port.write.called)

    def test_numeric_command_too_high(self):
        """Test that numeric command above 9 raises ValueError."""
        with self.assertRaises(ValueError):
            self.engine.numeric_command(23, 10)

    def test_numeric_command_too_low(self):
        """Test that numeric command below 0 raises ValueError."""
        with self.assertRaises(ValueError):
            self.engine.numeric_command(23, -1)

    # -------------------------
    # AUX command tests
    # -------------------------

    def test_aux1_off(self):
        """Test that aux1() with 'off' sends correct command packet."""
        self.engine.aux1(23, 'off')
        self.engine.port.write.assert_called_once_with(
            self._expected_packet(23, self.engine.ACTION, self.engine.AUX1_OFF)
        )

    def test_aux1_option1(self):
        """Test that aux1() with 'option1' sends correct command packet."""
        self.engine.aux1(23, 'option1')
        self.engine.port.write.assert_called_once_with(
            self._expected_packet(23, self.engine.ACTION, self.engine.AUX1_OPTION_1)
        )

    def test_aux1_option2(self):
        """Test that aux1() with 'option2' sends correct command packet."""
        self.engine.aux1(23, 'option2')
        self.engine.port.write.assert_called_once_with(
            self._expected_packet(23, self.engine.ACTION, self.engine.AUX1_OPTION_2)
        )

    def test_aux1_on(self):
        """Test that aux1() with 'on' sends correct command packet."""
        self.engine.aux1(23, 'on')
        self.engine.port.write.assert_called_once_with(
            self._expected_packet(23, self.engine.ACTION, self.engine.AUX1_ON)
        )

    def test_aux1_invalid(self):
        """Test that invalid AUX1 state raises ValueError."""
        with self.assertRaises(ValueError):
            self.engine.aux1(23, 'invalid')

    def test_aux2_off(self):
        """Test that aux2() with 'off' sends correct command packet."""
        self.engine.aux2(23, 'off')
        self.engine.port.write.assert_called_once_with(
            self._expected_packet(23, self.engine.ACTION, self.engine.AUX2_OFF)
        )

    def test_aux2_option1(self):
        """Test that aux2() with 'option1' sends correct command packet."""
        self.engine.aux2(23, 'option1')
        self.engine.port.write.assert_called_once_with(
            self._expected_packet(23, self.engine.ACTION, self.engine.AUX2_OPTION_1)
        )

    def test_aux2_option2(self):
        """Test that aux2() with 'option2' sends correct command packet."""
        self.engine.aux2(23, 'option2')
        self.engine.port.write.assert_called_once_with(
            self._expected_packet(23, self.engine.ACTION, self.engine.AUX2_OPTION_2)
        )

    def test_aux2_on(self):
        """Test that aux2() with 'on' sends correct command packet."""
        self.engine.aux2(23, 'on')
        self.engine.port.write.assert_called_once_with(
            self._expected_packet(23, self.engine.ACTION, self.engine.AUX2_ON)
        )

    def test_aux2_invalid(self):
        """Test that invalid AUX2 state raises ValueError."""
        with self.assertRaises(ValueError):
            self.engine.aux2(23, 'invalid')


if __name__ == '__main__':
    unittest.main()
