import unittest

import Chip6502 as chip
import NesMemory as memory

import Tests.Util.Register as register

class BaseTest(unittest.TestCase):

    def setUp(self):
        def init_register_functions():
            self.get_accumulator = register.get_accumulator_func(self.target)
            self.set_accumulator = register.set_accumulator_func(self.target)
            self.set_x_register = register.set_x_register_func(self.target)
            self.set_y_register = register.set_y_register_func(self.target)

        self.memory = memory.NesMemory(0xFFFF)
        self.target = chip.Chip6502(self.memory)
        init_register_functions()

    def prepare_absolute_operation(self, memory_value):
        self.memory.set_address(0x03, memory_value)

    def prepare_absolute_indexed_operation(self, operand):
        self.memory.set_address(0x04, operand)
        self.set_x_register(0x02)
        
    def prepare_indexed_indirect_operation(self, memory_value):
        self.set_x_register(0x02)

        self.memory.set_address(0x05, 0x02)
        self.memory.set_address(0x06, 0x03)
        self.memory.set_address(0x0302, memory_value)

    def prepare_indirect_indexed_operation(self, operand):
        self.set_y_register(0x02)

        self.memory.set_address(0x03, 0x08)
        self.memory.set_address(0x04, 0x0F)
        self.memory.set_address(0x0F0A, operand)
