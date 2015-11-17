import unittest

import Chip6502 as chip
import NesMemory as memory

class BaseTest(unittest.TestCase):

    def setUp(self):
        self.memory = memory.NesMemory(0xFFFF)
        self.target = chip.Chip6502(self.memory)
