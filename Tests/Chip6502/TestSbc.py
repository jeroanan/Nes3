import unittest

import Chip6502 as chip
import NesMemory as memory
import Tests.Util.Register as register
import Tests.Util.Flag as flag

class TestSbc(unittest.TestCase):

    def setUp(self):
        self.__memory = memory.NesMemory(0xFFFF)
        self.__target = chip.Chip6502(self.__memory)

        self.__set_accumulator = register.set_accumulator_func(self.__target)
        self.__get_accumulator = register.get_accumulator_func(self.__target)

        self.__set_accumulator(0x05)

    def test_sbc_immediate_subtracts_numbers(self):
        self.__target.sbc_immediate(0x02)
        self.assertEqual(0x03, self.__get_accumulator())
