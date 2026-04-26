import unittest
from tmcc.tmcc_command_factory import TMCCCommandFactory, DecodedCommand
from tmcc.tmcc_enums import CommandType, EngineAction


class TestEngineDecoder(unittest.TestCase):
    """
    Unit tests for decoding TMCC engine command packets.

    Tests that the TMCCCommandFactory correctly decodes all
    engine command types including direction, speed, sound,
    coupler, AUX, momentum, and numeric commands.
    """

    # -------------------------
    # Helper methods
    # -------------------------

    def _make_packet(self, word):
        """
        Helper to build a 3-byte TMCC packet from a 16-bit word.

        Args:
            word (int): 16-bit command word

        Returns:
            bytes: 3-byte TMCC packet
        """
        high_byte = (word >> 8) & 0xFF
        low_byte = word & 0xFF
        return bytes([0xFE, high_byte, low_byte])

    def _engine_word(self, address, command_field, data_field):
        """
        Helper to build a 16-bit engine command word.

        Args:
            address (int): Engine ID (1-99)
            command_field (int): 2-bit command field
            data_field (int): 5-bit data field

        Returns:
            int: 16-bit engine command word
        """
        return (address << 7) | (command_field << 5) | data_field

    # -------------------------
    # Command type tests
    # -------------------------

    def test_decode_engine_command_type(self):
        """Test that engine command type is CommandType.ENGINE."""
        packet = self._make_packet(self._engine_word(23, 0b00, 0b00000))
        result = TMCCCommandFactory.decode(packet)
        self.assertEqual(result.command_type, CommandType.ENGINE)

    def test_decode_engine_returns_decoded_command(self):
        """Test that decode() returns a DecodedCommand object."""
        packet = self._make_packet(self._engine_word(23, 0b00, 0b00000))
        result = TMCCCommandFactory.decode(packet)
        self.assertIsInstance(result, DecodedCommand)

    # -------------------------
    # Address tests
    # -------------------------

    def test_decode_engine_address_min(self):
        """Test that minimum engine address (1) is correctly decoded."""
        packet = self._make_packet(self._engine_word(1, 0b00, 0b00000))
        result = TMCCCommandFactory.decode(packet)
        self.assertEqual(result.address, 1)

    def test_decode_engine_address_max(self):
        """Test that maximum engine address (99) is correctly decoded."""
        packet = self._make_packet(self._engine_word(99, 0b00, 0b00000))
        result = TMCCCommandFactory.decode(packet)
        self.assertEqual(result.address, 99)

    def test_decode_engine_address_mid(self):
        """Test that mid-range engine address (23) is correctly decoded."""
        packet = self._make_packet(self._engine_word(23, 0b00, 0b00000))
        result = TMCCCommandFactory.decode(packet)
        self.assertEqual(result.address, 23)

    # -------------------------
    # Direction command tests
    # -------------------------

    def test_decode_engine_forward(self):
        """Test decoding of engine forward command."""
        packet = self._make_packet(self._engine_word(23, 0b00, 0b00000))
        result = TMCCCommandFactory.decode(packet)
        self.assertEqual(result.action, EngineAction.FORWARD)

    def test_decode_engine_reverse(self):
        """Test decoding of engine reverse command."""
        packet = self._make_packet(self._engine_word(23, 0b00, 0b00011))
        result = TMCCCommandFactory.decode(packet)
        self.assertEqual(result.action, EngineAction.REVERSE)

    def test_decode_engine_toggle_direction(self):
        """Test decoding of engine toggle direction command."""
        packet = self._make_packet(self._engine_word(23, 0b00, 0b00001))
        result = TMCCCommandFactory.decode(packet)
        self.assertEqual(result.action, EngineAction.TOGGLE_DIR)

    # -------------------------
    # Boost and brake tests
    # -------------------------

    def test_decode_engine_boost(self):
        """Test decoding of engine boost command."""
        packet = self._make_packet(self._engine_word(23, 0b00, 0b00100))
        result = TMCCCommandFactory.decode(packet)
        self.assertEqual(result.action, EngineAction.BOOST)

    def test_decode_engine_brake(self):
        """Test decoding of engine brake command."""
        packet = self._make_packet(self._engine_word(23, 0b00, 0b00111))
        result = TMCCCommandFactory.decode(packet)
        self.assertEqual(result.action, EngineAction.BRAKE)

    # -------------------------
    # Sound command tests
    # -------------------------

    def test_decode_engine_blow_horn_1(self):
        """Test decoding of engine horn 1 command."""
        packet = self._make_packet(self._engine_word(23, 0b00, 0b11100))
        result = TMCCCommandFactory.decode(packet)
        self.assertEqual(result.action, EngineAction.BLOW_HORN_1)

    def test_decode_engine_blow_horn_2(self):
        """Test decoding of engine horn 2 command."""
        packet = self._make_packet(self._engine_word(23, 0b00, 0b11111))
        result = TMCCCommandFactory.decode(packet)
        self.assertEqual(result.action, EngineAction.BLOW_HORN_2)

    def test_decode_engine_ring_bell(self):
        """Test decoding of engine bell command."""
        packet = self._make_packet(self._engine_word(23, 0b00, 0b11101))
        result = TMCCCommandFactory.decode(packet)
        self.assertEqual(result.action, EngineAction.RING_BELL)

    def test_decode_engine_letoff(self):
        """Test decoding of engine letoff sound command."""
        packet = self._make_packet(self._engine_word(23, 0b00, 0b11110))
        result = TMCCCommandFactory.decode(packet)
        self.assertEqual(result.action, EngineAction.LETOFF)

    # -------------------------
    # Coupler command tests
    # -------------------------

    def test_decode_engine_open_front_coupler(self):
        """Test decoding of engine front coupler command."""
        packet = self._make_packet(self._engine_word(23, 0b00, 0b00101))
        result = TMCCCommandFactory.decode(packet)
        self.assertEqual(result.action, EngineAction.OPEN_FRONT_COUPLER)

    def test_decode_engine_open_rear_coupler(self):
        """Test decoding of engine rear coupler command."""
        packet = self._make_packet(self._engine_word(23, 0b00, 0b00110))
        result = TMCCCommandFactory.decode(packet)
        self.assertEqual(result.action, EngineAction.OPEN_REAR_COUPLER)

    # -------------------------
    # AUX1 command tests
    # -------------------------

    def test_decode_engine_aux1_off(self):
        """Test decoding of engine AUX1 off command."""
        packet = self._make_packet(self._engine_word(23, 0b00, 0b01000))
        result = TMCCCommandFactory.decode(packet)
        self.assertEqual(result.action, EngineAction.AUX1_OFF)

    def test_decode_engine_aux1_option1(self):
        """Test decoding of engine AUX1 option 1 command."""
        packet = self._make_packet(self._engine_word(23, 0b00, 0b01001))
        result = TMCCCommandFactory.decode(packet)
        self.assertEqual(result.action, EngineAction.AUX1_OPTION_1)

    def test_decode_engine_aux1_option2(self):
        """Test decoding of engine AUX1 option 2 command."""
        packet = self._make_packet(self._engine_word(23, 0b00, 0b01010))
        result = TMCCCommandFactory.decode(packet)
        self.assertEqual(result.action, EngineAction.AUX1_OPTION_2)

    def test_decode_engine_aux1_on(self):
        """Test decoding of engine AUX1 on command."""
        packet = self._make_packet(self._engine_word(23, 0b00, 0b01011))
        result = TMCCCommandFactory.decode(packet)
        self.assertEqual(result.action, EngineAction.AUX1_ON)

    # -------------------------
    # AUX2 command tests
    # -------------------------

    def test_decode_engine_aux2_off(self):
        """Test decoding of engine AUX2 off command."""
        packet = self._make_packet(self._engine_word(23, 0b00, 0b01100))
        result = TMCCCommandFactory.decode(packet)
        self.assertEqual(result.action, EngineAction.AUX2_OFF)

    def test_decode_engine_aux2_option1(self):
        """Test decoding of engine AUX2 option 1 command."""
        packet = self._make_packet(self._engine_word(23, 0b00, 0b01101))
        result = TMCCCommandFactory.decode(packet)
        self.assertEqual(result.action, EngineAction.AUX2_OPTION_1)

    def test_decode_engine_aux2_option2(self):
        """Test decoding of engine AUX2 option 2 command."""
        packet = self._make_packet(self._engine_word(23, 0b00, 0b01110))
        result = TMCCCommandFactory.decode(packet)
        self.assertEqual(result.action, EngineAction.AUX2_OPTION_2)

    def test_decode_engine_aux2_on(self):
        """Test decoding of engine AUX2 on command."""
        packet = self._make_packet(self._engine_word(23, 0b00, 0b01111))
        result = TMCCCommandFactory.decode(packet)
        self.assertEqual(result.action, EngineAction.AUX2_ON)

    # -------------------------
    # Momentum command tests
    # -------------------------

    def test_decode_engine_momentum_low(self):
        """Test decoding of engine momentum low command."""
        packet = self._make_packet(self._engine_word(23, 0b01, 0b01000))
        result = TMCCCommandFactory.decode(packet)
        self.assertEqual(result.action, EngineAction.MOMENTUM_LOW)

    def test_decode_engine_momentum_medium(self):
        """Test decoding of engine momentum medium command."""
        packet = self._make_packet(self._engine_word(23, 0b01, 0b01001))
        result = TMCCCommandFactory.decode(packet)
        self.assertEqual(result.action, EngineAction.MOMENTUM_MEDIUM)

    def test_decode_engine_momentum_high(self):
        """Test decoding of engine momentum high command."""
        packet = self._make_packet(self._engine_word(23, 0b01, 0b01010))
        result = TMCCCommandFactory.decode(packet)
        self.assertEqual(result.action, EngineAction.MOMENTUM_HIGH)

    # -------------------------
    # Numeric command tests
    # -------------------------

    def test_decode_engine_numeric_0(self):
        """Test decoding of engine numeric command 0."""
        packet = self._make_packet(self._engine_word(23, 0b00, 0b10000))
        result = TMCCCommandFactory.decode(packet)
        self.assertEqual(result.action, EngineAction.NUMERIC_0)

    def test_decode_engine_numeric_1(self):
        """Test decoding of engine numeric command 1."""
        packet = self._make_packet(self._engine_word(23, 0b00, 0b10001))
        result = TMCCCommandFactory.decode(packet)
        self.assertEqual(result.action, EngineAction.NUMERIC_1)

    def test_decode_engine_numeric_2(self):
        """Test decoding of engine numeric command 2."""
        packet = self._make_packet(self._engine_word(23, 0b00, 0b10010))
        result = TMCCCommandFactory.decode(packet)
        self.assertEqual(result.action, EngineAction.NUMERIC_2)

    def test_decode_engine_numeric_3(self):
        """Test decoding of engine numeric command 3."""
        packet = self._make_packet(self._engine_word(23, 0b00, 0b10011))
        result = TMCCCommandFactory.decode(packet)
        self.assertEqual(result.action, EngineAction.NUMERIC_3)

    def test_decode_engine_numeric_4(self):
        """Test decoding of engine numeric command 4."""
        packet = self._make_packet(self._engine_word(23, 0b00, 0b10100))
        result = TMCCCommandFactory.decode(packet)
        self.assertEqual(result.action, EngineAction.NUMERIC_4)

    def test_decode_engine_numeric_5(self):
        """Test decoding of engine numeric command 5."""
        packet = self._make_packet(self._engine_word(23, 0b00, 0b10101))
        result = TMCCCommandFactory.decode(packet)
        self.assertEqual(result.action, EngineAction.NUMERIC_5)

    def test_decode_engine_numeric_6(self):
        """Test decoding of engine numeric command 6."""
        packet = self._make_packet(self._engine_word(23, 0b00, 0b10110))
        result = TMCCCommandFactory.decode(packet)
        self.assertEqual(result.action, EngineAction.NUMERIC_6)

    def test_decode_engine_numeric_7(self):
        """Test decoding of engine numeric command 7."""
        packet = self._make_packet(self._engine_word(23, 0b00, 0b10111))
        result = TMCCCommandFactory.decode(packet)
        self.assertEqual(result.action, EngineAction.NUMERIC_7)

    def test_decode_engine_numeric_8(self):
        """Test decoding of engine numeric command 8."""
        packet = self._make_packet(self._engine_word(23, 0b00, 0b11000))
        result = TMCCCommandFactory.decode(packet)
        self.assertEqual(result.action, EngineAction.NUMERIC_8)

    def test_decode_engine_numeric_9(self):
        """Test decoding of engine numeric command 9."""
        packet = self._make_packet(self._engine_word(23, 0b00, 0b11001))
        result = TMCCCommandFactory.decode(packet)
        self.assertEqual(result.action, EngineAction.NUMERIC_9)

    # -------------------------
    # Absolute speed tests
    # -------------------------

    def test_decode_engine_absolute_speed_action(self):
        """Test that absolute speed action is EngineAction.ABSOLUTE_SPEED."""
        packet = self._make_packet(self._engine_word(23, 0b11, 15))
        result = TMCCCommandFactory.decode(packet)
        self.assertEqual(result.action, EngineAction.ABSOLUTE_SPEED)

    def test_decode_engine_absolute_speed_value(self):
        """Test that absolute speed value is correctly decoded."""
        packet = self._make_packet(self._engine_word(23, 0b11, 15))
        result = TMCCCommandFactory.decode(packet)
        self.assertEqual(result.speed_value, 15)

    def test_decode_engine_absolute_speed_zero(self):
        """Test decoding of engine absolute speed 0."""
        packet = self._make_packet(self._engine_word(23, 0b11, 0))
        result = TMCCCommandFactory.decode(packet)
        self.assertEqual(result.speed_value, 0)

    def test_decode_engine_absolute_speed_max(self):
        """Test decoding of engine absolute speed 31."""
        packet = self._make_packet(self._engine_word(23, 0b11, 31))
        result = TMCCCommandFactory.decode(packet)
        self.assertEqual(result.speed_value, 31)

    # -------------------------
    # Relative speed tests
    # -------------------------

    def test_decode_engine_relative_speed_action(self):
        """Test that relative speed action is EngineAction.RELATIVE_SPEED."""
        packet = self._make_packet(self._engine_word(23, 0b10, 3 + 5))
        result = TMCCCommandFactory.decode(packet)
        self.assertEqual(result.action, EngineAction.RELATIVE_SPEED)

    def test_decode_engine_relative_speed_positive(self):
        """Test decoding of engine positive relative speed command."""
        packet = self._make_packet(self._engine_word(23, 0b10, 3 + 5))
        result = TMCCCommandFactory.decode(packet)
        self.assertEqual(result.speed_value, 3)

    def test_decode_engine_relative_speed_negative(self):
        """Test decoding of engine negative relative speed command."""
        packet = self._make_packet(self._engine_word(23, 0b10, -3 + 5))
        result = TMCCCommandFactory.decode(packet)
        self.assertEqual(result.speed_value, -3)

    def test_decode_engine_relative_speed_zero(self):
        """Test decoding of engine zero relative speed command."""
        packet = self._make_packet(self._engine_word(23, 0b10, 5))
        result = TMCCCommandFactory.decode(packet)
        self.assertEqual(result.speed_value, 0)

    def test_decode_engine_relative_speed_max(self):
        """Test decoding of engine max relative speed (+5)."""
        packet = self._make_packet(self._engine_word(23, 0b10, 5 + 5))
        result = TMCCCommandFactory.decode(packet)
        self.assertEqual(result.speed_value, 5)

    def test_decode_engine_relative_speed_min(self):
        """Test decoding of engine min relative speed (-5)."""
        packet = self._make_packet(self._engine_word(23, 0b10, -5 + 5))
        result = TMCCCommandFactory.decode(packet)
        self.assertEqual(result.speed_value, -5)

    # -------------------------
    # Speed value tests
    # -------------------------

    def test_decoded_engine_speed_value_none_for_non_speed(self):
        """Test that speed_value is None for non-speed commands."""
        packet = self._make_packet(self._engine_word(23, 0b00, 0b00000))
        result = TMCCCommandFactory.decode(packet)
        self.assertIsNone(result.speed_value)

    def test_decoded_engine_speed_value_set_for_absolute_speed(self):
        """Test that speed_value is set for absolute speed commands."""
        packet = self._make_packet(self._engine_word(23, 0b11, 15))
        result = TMCCCommandFactory.decode(packet)
        self.assertIsNotNone(result.speed_value)

    def test_decoded_engine_speed_value_set_for_relative_speed(self):
        """Test that speed_value is set for relative speed commands."""
        packet = self._make_packet(self._engine_word(23, 0b10, 3 + 5))
        result = TMCCCommandFactory.decode(packet)
        self.assertIsNotNone(result.speed_value)

    # -------------------------
    # Description tests
    # -------------------------

    def test_decode_engine_description_forward(self):
        """Test that engine forward description is correctly formatted."""
        packet = self._make_packet(self._engine_word(23, 0b00, 0b00000))
        result = TMCCCommandFactory.decode(packet)
        self.assertEqual(result.description, "Engine 23: Forward")

    def test_decode_engine_description_absolute_speed(self):
        """Test that engine absolute speed description is correctly formatted."""
        packet = self._make_packet(self._engine_word(23, 0b11, 15))
        result = TMCCCommandFactory.decode(packet)
        self.assertEqual(result.description, "Engine 23: Absolute Speed 15")

    def test_decode_engine_description_relative_speed_positive(self):
        """Test that engine positive relative speed description is correctly formatted."""
        packet = self._make_packet(self._engine_word(23, 0b10, 3 + 5))
        result = TMCCCommandFactory.decode(packet)
        self.assertEqual(result.description, "Engine 23: Relative Speed +3")

    def test_decode_engine_description_relative_speed_negative(self):
        """Test that engine negative relative speed description is correctly formatted."""
        packet = self._make_packet(self._engine_word(23, 0b10, -3 + 5))
        result = TMCCCommandFactory.decode(packet)
        self.assertEqual(result.description, "Engine 23: Relative Speed -3")

    def test_decode_engine_description_relative_speed_zero(self):
        """Test that engine zero relative speed description is correctly formatted."""
        packet = self._make_packet(self._engine_word(23, 0b10, 5))
        result = TMCCCommandFactory.decode(packet)
        self.assertEqual(result.description, "Engine 23: Relative Speed +0")


if __name__ == '__main__':
    unittest.main()

