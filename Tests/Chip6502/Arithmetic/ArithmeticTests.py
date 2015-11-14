import unittest

import Chip6502 as chip
import NesMemory as memory
import Tests.Util.Register as register
import Tests.Util.Flag as flag

class ArithmeticTests(unittest.TestCase):
    def setUp(self):
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
