import unittest

import Chip6502 as chip
import NesMemory as memory
import Tests.Util.Register as register
import Tests.Util.Flag as flag

class TestSbc(unittest.TestCase):

    def setUp(self):
        self.__memory = memory.NesMemory(0xFFFF)
        self.__target = chip.Chip6502(self.__memory)
