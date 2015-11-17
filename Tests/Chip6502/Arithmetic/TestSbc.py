import unittest
import Tests.Chip6502.Arithmetic.ArithmeticTests as at

class TestSbc(at.ArithmeticTests):

    def setUp(self):
        super().setUp()

        self.__init_accumulator = lambda: self.set_accumulator(0x05)
        self.__init_accumulator()

        self.__subtraction_funcs = {
            "do_immediate_subtraction": self.__do_immediate_subtraction,
            "do_absolute_subtraction": self.__do_absolute_subtraction,
            "do_absolute_indexed_subtraction": self.__do_absolute_indexed_subtraction,
            "do_indexed_indirect_subtraction": self.__do_indexed_indirect_subtraction,
            "do_indirect_indexed_subtraction": self.__do_indirect_indexed_subtraction
        }

    def test_sbc_subtracts_numbers(self):
        for func_name, subtraction_func in self.__subtraction_funcs.items():
            self.set_carry_flag()
            self.__init_accumulator()
            subtraction_func(operand=0x02)
            expected_result = 0x03
            actual_result = self.get_accumulator()
            self.assertEqual(expected_result,
                             actual_result,
                             "Got {result} while executing {fn}. Expected {expected}.".format(result=actual_result,
                                                                                              fn=func_name,
                                                                                              expected=expected_result))

    def test_sbc_sets_carry_flag_when_necessary(self):
        accumulator_value = 0x04

        operand_carry_flag_mappings = {
            0x06: 0x00,
            0x03: 0x01
        }

        for func_name, subtraction_func in self.__subtraction_funcs.items():
            for operand, flag_value in operand_carry_flag_mappings.items():

                self.set_accumulator(accumulator_value)

                if func_name == "do_immediate_subtraction":
                    subtraction_func(operand=operand, accumulator_value=accumulator_value)
                else:
                    subtraction_func(operand=operand)

                actual_flag_value = self.target.carry_flag

                self.assertEqual(flag_value,
                                 actual_flag_value,
                                 """Expected carry flag value of {cf} when subtracting {op} from {av} using {fn}.
                                 Got {fv}."""
                                 .format(cf=flag_value,
                                         av=accumulator_value,
                                         op=operand,
                                         fn=func_name,
                                         fv=actual_flag_value))

    def test_sbc_subtracts_carry_flag(self):

        for func_name, subtraction_func in self.__subtraction_funcs.items():
            self.__init_accumulator()
            operand = 0x01
            self.clear_carry_flag()
            expected_result = 0x03

            subtraction_func(operand)
            self.assertEqual(expected_result,
                             self.get_accumulator(),
                             "Expected {ex} when executing {fn}. Got {ac}.".format(ex=expected_result,
                                                                                   fn=func_name,
                                                                                   ac=self.get_accumulator()))

    def test_sbc_sets_overflow_flag(self):
        pass

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
