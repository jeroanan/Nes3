import unittest

import Tests.Chip6502.BaseTest as base_test
import Chip6502 as chip
import NesMemory as memory

import Tests.Util.Flag as flag

class ArithmeticTests(base_test.BaseTest):

    def setUp(self):
        super().setUp()
        self.arithmetic_funcs = {'': ''}

        def init_flag_functions():
            self.set_carry_flag = flag.set_carry_flag_func(self.target)
            self.clear_carry_flag = flag.clear_carry_flag_func(self.target)
            self.set_overflow_flag = flag.set_overflow_flag_func(self.target)
            self.clear_overflow_flag = flag.clear_overflow_flag_func(self.target)
            self.get_overflow_flag = flag.get_overflow_flag_func(self.target)

        init_flag_functions()    

    def assert_overflow_flag(self, overflow_flag_init_func, operand, expected_result, initial_accumulator_val):

        for func_name, arithmetic_func in self.arithmetic_funcs.items():
            self.set_accumulator(initial_accumulator_val)
            overflow_flag_init_func()
            arithmetic_func(operand)
            self.assertEqual(expected_result,
                             self.get_overflow_flag(),
                             "Overflow flag not correct when executing {f}. Expected {x}. Got {a}."
                             .format(f=func_name, x=expected_result, a=self.get_overflow_flag()))

    def assert_carry_flag(self, accumulator_value, operand_carry_flag_mappings):
        for func_name, arithmetic_func in self.arithmetic_funcs.items():
            for operand, flag_value in operand_carry_flag_mappings.items():

                self.set_accumulator(accumulator_value)

                if func_name == "do_immediate_add":
                    arithmetic_func(operand=operand, accumulator_value=accumulator_value)
                else:
                    arithmetic_func(operand=operand)

                actual_flag_value = self.target.carry_flag

                self.assertEqual(flag_value,
                                 actual_flag_value,
                                 "Expected carry flag value of {cf} when adding {av} and {op} using {fn}. Got {fv}."
                                 .format(cf=flag_value,
                                         av=accumulator_value,
                                         op=operand,
                                         fn=func_name,
                                         fv=actual_flag_value))

    def assert_uses_carry_flag(self, init_carry_flag_func, init_accumulator_func):
         operand = 0x01
         expected_result = 0x03

         for func_name, arithmetic_func in self.arithmetic_funcs.items():
             init_accumulator_func()
             init_carry_flag_func()
             arithmetic_func(operand)
             self.assertEqual(expected_result,
                              self.get_accumulator(),
                              "Expected {ex} when executing {fn}. Got {ac}.".format(ex=expected_result,
                                                                                    fn=func_name,
                                                                                    ac=self.get_accumulator()))

    def assert_performs_arithmetic(self, init_carry_flag_func, init_accumulator_func):
        expected_value = 0x03

        for func_name, arithmetic_func in self.arithmetic_funcs.items():
            init_carry_flag_func()
            init_accumulator_func()
            arithmetic_func(operand=0x02)
            self.assertEqual(expected_value,
                             self.get_accumulator(),
                             "Expected value {ex} when executing {fn}. Got {ac}".format(ex=expected_value,
                                                                                        fn=func_name,
                                                                                        ac=self.get_accumulator()))
