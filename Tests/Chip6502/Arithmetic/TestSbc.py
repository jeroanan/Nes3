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
            self.__init_accumulator()
            subtraction_func(operand=0x02)
            expected_result = 0x03
            actual_result = self.get_accumulator()
            self.assertEqual(expected_result,
                             actual_result,
                             "Got {result} while executing {fn}. Expected {expected}.".format(result=actual_result,
                                                                                              fn=func_name,
                                                                                              expected=expected_result))

    def __do_immediate_subtraction(self, operand):
        self.target.sbc_immediate(operand)

    def __do_absolute_subtraction(self, operand):
        self.memory.set_address(0x03, operand)
        self.target.sbc_absolute(0x03)

    def __do_absolute_indexed_subtraction(self, operand):
        self.memory.set_address(0x04, operand)
        self.set_x_register(0x02)
        self.target.sbc_absolute_indexed(0x02, 'X')

    def __do_indexed_indirect_subtraction(self, operand):
        self.set_x_register(0x02)
        base_address = 0x03

        self.memory.set_address(0x05, 0x02)
        self.memory.set_address(0x06, 0x03)
        self.memory.set_address(0x0302, operand)

        self.target.sbc_indexed_indirect(base_address)

    def __do_indirect_indexed_subtraction(self, operand):
        self.set_y_register(0x02)
        base_address = 0x03

        self.memory.set_address(0x03, 0x08)
        self.memory.set_address(0x04, 0x0F)
        self.memory.set_address(0x0F0A, operand)

        self.target.sbc_indirect_indexed(base_address)
