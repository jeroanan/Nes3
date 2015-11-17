import unittest

import Chip6502 as chip
import NesMemory as memory
import Tests.Util.Register as register
import Tests.Util.Flag as flag

class ArithmeticTests(unittest.TestCase):
    def setUp(self):

        self.arithmetic_funcs = {'': ''}

        self.memory = memory.NesMemory(0xFFFF)
        self.target = chip.Chip6502(self.memory)

        def init_register_functions():
            self.get_accumulator = register.get_accumulator_func(self.target)
            self.set_accumulator = register.set_accumulator_func(self.target)
            self.set_x_register = register.set_x_register_func(self.target)
            self.set_y_register = register.set_y_register_func(self.target)

        def init_flag_functions():
            self.set_carry_flag = flag.set_carry_flag_func(self.target)
            self.clear_carry_flag = flag.clear_carry_flag_func(self.target)
            self.set_overflow_flag = flag.set_overflow_flag_func(self.target)
            self.clear_overflow_flag = flag.clear_overflow_flag_func(self.target)
            self.get_overflow_flag = flag.get_overflow_flag_func(self.target)

        init_register_functions()
        init_flag_functions()

    def prepare_absolute_operation(self, operand):
        self.memory.set_address(0x03, operand)

    def prepare_absolute_indexed_operation(self, operand):
        self.memory.set_address(0x04, operand)
        self.set_x_register(0x02)

    def prepare_indexed_indirect_operation(self, operand):
        self.set_x_register(0x02)

        self.memory.set_address(0x05, 0x02)
        self.memory.set_address(0x06, 0x03)
        self.memory.set_address(0x0302, operand)

    def prepare_indirect_indexed_operation(self, operand):
        self.set_y_register(0x02)

        self.memory.set_address(0x03, 0x08)
        self.memory.set_address(0x04, 0x0F)
        self.memory.set_address(0x0F0A, operand)

    def assert_overflow_flag(self, overflow_flag_init_func, operand, expected_result, initial_accumulator_val):

        for func_name, subtraction_func in self.arithmetic_funcs.items():
            self.set_accumulator(initial_accumulator_val)
            overflow_flag_init_func()
            subtraction_func(operand)
            self.assertEqual(expected_result,
                             self.get_overflow_flag(),
                             "Overflow flag not correct when executing {f}. Expected {x}. Got {a}."
                             .format(f=func_name, x=expected_result, a=self.get_overflow_flag()))
