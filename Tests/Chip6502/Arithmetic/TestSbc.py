import unittest
import Tests.Chip6502.Arithmetic.ArithmeticTests as at

class TestSbc(at.ArithmeticTests):

    def setUp(self):
        super().setUp()

        self.__init_accumulator = lambda: self.set_accumulator(0x05)
        self.__init_accumulator()

        self.arithmetic_funcs = {
            "do_immediate_subtraction": self.__do_immediate_subtraction,
            "do_absolute_subtraction": self.__do_absolute_subtraction,
            "do_absolute_indexed_subtraction": self.__do_absolute_indexed_subtraction,
            "do_indexed_indirect_subtraction": self.__do_indexed_indirect_subtraction,
            "do_indirect_indexed_subtraction": self.__do_indirect_indexed_subtraction
        }

    def test_sbc_subtracts_numbers(self):
        self.assert_performs_arithmetic(self.set_carry_flag, self.__init_accumulator)

    def test_sbc_sets_carry_flag_when_necessary(self):
        accumulator_value = 0x04

        operand_carry_flag_mappings = {
            0x06: 0x00,
            0x03: 0x01
        }

        self.assert_carry_flag(accumulator_value, operand_carry_flag_mappings)

    def test_sbc_subtracts_carry_flag(self):
        self.assert_uses_carry_flag(self.clear_carry_flag, self.__init_accumulator)

    def test_sbc_sets_overflow_flag(self):
        self.assert_overflow_flag(self.clear_overflow_flag, 0x80, 0x01, 0xFF)

    def test_sgc_clears_overflow_flag(self):
        self.assert_overflow_flag(self.set_overflow_flag, 0x01, 0x00, 0xFF)

    def __do_immediate_subtraction(self, operand, accumulator_value=0x05):
        self.set_accumulator(accumulator_value)
        self.target.sbc_immediate(operand)

    def __do_absolute_subtraction(self, operand):
        self.prepare_absolute_operation(operand)
        self.target.sbc_absolute(0x03)

    def __do_absolute_indexed_subtraction(self, operand):
        self.prepare_absolute_indexed_operation(operand)
        self.target.sbc_absolute_indexed(0x02, 'X')

    def __do_indexed_indirect_subtraction(self, operand):
        base_address = 0x03
        self.prepare_indexed_indirect_operation(operand)
        self.target.sbc_indexed_indirect(base_address)

    def __do_indirect_indexed_subtraction(self, operand):
        base_address = 0x03
        self.prepare_indirect_indexed_operation(operand)
        self.target.sbc_indirect_indexed(base_address)
