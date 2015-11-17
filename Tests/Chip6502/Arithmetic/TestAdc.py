import unittest
import Tests.Chip6502.Arithmetic.ArithmeticTests as at

class TestAdc(at.ArithmeticTests):

    def setUp(self):

        super().setUp()

        self.__init_accumulator = lambda: self.set_accumulator(0x01)
        self.__init_accumulator()

        self.arithmetic_funcs = {
            "do_immediate_add": self.__do_immediate_add,
            "do_absolute_add": self.__do_absolute_add,
            "do_absolute_indexed_add": self.__do_absolute_indexed_add,
            "do_indexed_indirect_add": self.__do_indexed_indirect_add,
            "do_indirect_indexed_add": self.__do_indirect_indexed_add
        }

    def test_adc_adds_numbers(self):
        expected_value = 0x03

        for func_name, addition_func in self.arithmetic_funcs.items():
            self.__init_accumulator()
            addition_func(operand=0x02)
            self.assertEqual(expected_value,
                             self.get_accumulator(),
                             "Expected value {ex} when executing {fn}. Got {ac}".format(ex=expected_value,
                                                                                        fn=func_name,
                                                                                        ac=self.get_accumulator()))

    def test_adc_sets_carry_flag_when_necessary(self):
        accumulator_value = 0xFD

        operand_carry_flag_mappings = {
            0x03: 0x01,
            0x01: 0x00
        }

        self.assert_carry_flag(accumulator_value, operand_carry_flag_mappings)

    def test_adc_adds_carry_flag(self):
        self.assert_uses_carry_flag(self.set_carry_flag, self.__init_accumulator)

    def test_adc_sets_overflow_flag(self):
        """
        Test that when an addition operation takes place that causes the accumulator's seventh bit (the sign bit) to
        change value, the overflow flag is set.
        """
        self.assert_overflow_flag(self.clear_overflow_flag, 0x7F, 0x01, 0x01)

    def test_adc_clears_overflow_flag(self):
        """
        Test that when an addition operation takes place that does not cause the accumulator's seventh bit (the sign
        bit) to change value, the overflow flag is cleared.
        """
        self.assert_overflow_flag(self.set_overflow_flag, 0x01, 0x00, 0x01)

    def __do_immediate_add(self, accumulator_value=0x01, operand=0x01):
        self.set_accumulator(accumulator_value)
        self.target.adc_immediate(operand)

    def __do_absolute_add(self, operand):
        self.prepare_absolute_operation(operand)
        self.target.adc_absolute(0x03)

    def __do_absolute_indexed_add(self, operand):
        self.prepare_absolute_indexed_operation(operand)
        self.target.adc_absolute_indexed(0x02, 'X')

    def __do_indexed_indirect_add(self, operand):
        base_address = 0x03
        self.prepare_indexed_indirect_operation(operand)
        self.target.adc_indexed_indirect(base_address)

    def __do_indirect_indexed_add(self, operand):
        base_address = 0x03
        self.prepare_indirect_indexed_operation(operand)
        self.target.adc_indirect_indexed(base_address)
