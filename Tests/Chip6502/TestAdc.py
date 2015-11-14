import unittest

import Chip6502 as chip
import NesMemory as memory
import Tests.Util.Register as register
import Tests.Util.Flag as flag

class TestAdc(unittest.TestCase):

    def setUp(self):
        self.__memory = memory.NesMemory(0xFFFF)
        self.__target = chip.Chip6502(self.__memory)

        def init_register_functions():
            self.__get_accumulator = register.get_accumulator_func(self.__target)
            self.__set_accumulator = register.set_accumulator_func(self.__target)
            self.__set_x_register = register.set_x_register_func(self.__target)

        def init_flag_functions():
            self.__set_carry_flag = flag.set_carry_flag_func(self.__target)
            self.__clear_carry_flag = flag.clear_carry_flag_func(self.__target)
            self.__set_overflow_flag = flag.set_overflow_flag_func(self.__target)
            self.__clear_overflow_flag = flag.clear_overflow_flag_func(self.__target)
            self.__get_overflow_flag = flag.get_overflow_flag_func(self.__target)

        init_register_functions()
        init_flag_functions()
        self.__set_accumulator(0x01)

        self.__addition_funcs = {
            "do_immediate_add": self.__do_immediate_add,
            "do_absolute_add": self.__do_absolute_add,
            "do_absolute_indexed_add": self.__do_absolute_indexed_add,
            "do_indexed_indirect_add": self.__do_indexed_indirect_add
        }

    def test_adc_adds_numbers(self):
        expected_value = 0x03

        for func_name, func in self.__addition_funcs.items():
            self.__set_accumulator(0x01)
            func(operand=0x02)
            self.assertEqual(expected_value,
                             self.__get_accumulator(),
                             "Expected value {ex} when executing {fn}. Got {ac}".format(ex=expected_value,
                                                                                        fn=func_name,
                                                                                        ac=self.__get_accumulator()))

    def test_adc_sets_carry_flag_when_necessary(self):
        accumulator_value = 0xFD

        operand_carry_flag_mappings = {
            0x03: 0x01,
            0x01: 0x00
        }

        for func_name, addition_func in self.__addition_funcs.items():
            for operand, flag_value in operand_carry_flag_mappings.items():
                self.__do_immediate_add(accumulator_value, operand)
                actual_flag_value = self.__target.carry_flag

                self.assertEqual(flag_value,
                                 actual_flag_value,
                                 "Expected carry flag value of {cf} when adding {av} and {op} using {fn}. Got {fv}."
                                 .format(cf=flag_value,
                                         av=accumulator_value,
                                         op=operand,
                                         fn=func_name,
                                         fv=actual_flag_value))

    def test_adc_adds_carry_flag(self):

        for func_name, addition_func in self.__addition_funcs.items():
            self.__set_accumulator(0x01)
            operand = 0x01
            self.__set_carry_flag()
            expected_result = 0x03

            addition_func(operand)
            self.assertEqual(expected_result,
                             self.__get_accumulator(),
                             "Expected {ex} when executing {fn}. Got {ac}.".format(ex=expected_result,
                                                                                   fn=func_name,
                                                                                   ac=self.__get_accumulator()))

    def test_adc_sets_overflow_flag(self):
        """
        Test that when an addition operation takes place that causes the accumulator's seventh bit (the sign bit) to
        change value, the overflow flag is set.
        """
        self.__assert_overflow_flag(self.__clear_overflow_flag, 0x7F, 0x01)

    def test_adc_clears_overflow_flag(self):
        """
        Test that when an addition operation takes place that does not cause the accumulator's seventh bit (the sign
        bit) to change value, the overflow flag is cleared.
        """
        self.__assert_overflow_flag(self.__set_overflow_flag, 0x01, 0x00)

    def __assert_overflow_flag(self, overflow_flag_init_func, operand, expected_result):
        for func_name, addition_func in self.__addition_funcs.items():
            overflow_flag_init_func()
            self.__set_accumulator(0x01)

            addition_func(operand)
            self.assertEqual(expected_result,
                             self.__get_overflow_flag(),
                             "Expected {ex} when executing {fn}. Got: {of}".format(ex=expected_result,
                                                                                   fn=func_name,
                                                                                   of=self.__get_overflow_flag()))

    def __do_immediate_add(self, accumulator_value=0x01, operand=0x01):
        self.__set_accumulator(accumulator_value)
        self.__target.adc_immediate(operand)

    def __do_absolute_add(self, operand):
        self.__memory.set_address(0x03, operand)
        self.__target.adc_absolute(0x03)

    def __do_absolute_indexed_add(self, operand):
        self.__memory.set_address(0x04, operand)
        self.__set_x_register(0x02)
        self.__target.adc_absolute_indexed(0x02, 'X')

    def __do_indexed_indirect_add(self, operand):
        self.__set_x_register(0x02)
        base_address = 0x03

        self.__memory.set_address(0x05, 0x02)
        self.__memory.set_address(0x06, 0x03)
        self.__memory.set_address(0x0302, operand)

        self.__target.adc_indexed_indirect(base_address)
