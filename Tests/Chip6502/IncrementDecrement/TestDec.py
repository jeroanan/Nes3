import Tests.Chip6502.BaseTest as base_test

class TestDec(base_test.BaseTest):

    def setUp(self):
        super().setUp()

        self.__dec_funcs = {'dec_immediate': self.__do_dec_immediate,
                            'dec_absolute': self.__do_dec_absolute,
                            'dec_absolute_indexed': self.__do_dec_absolute_indexed,
                            'inc_indexed_indirect': self.__do_dec_indexed_indirect,
                            'dec_indirect_indexed': self.__do_dec_indirect_indexed}

        self.__init_memory = lambda: self.memory.set_address(self.__memory_address_to_decrement, 0x02)
        self.__memory_address_to_decrement = 0x01
        self.__init_memory()

    def test_dec_decrements_memory_value(self):
        expected_result = 0x01

        for func_name, func in self.__dec_funcs.items():
            self.__init_memory()
            func()
            actual_result = self.memory.get_address(self.__memory_address_to_decrement)
            self.assertEqual(expected_result,
                             actual_result,
                             "Incorrect memory value retrieved when executing {fn}. Expected {ex} but got {ar}."
                             .format(fn=func_name, ex=expected_result, ar=actual_result))

    def test_dec_sets_negative_flag(self):
        expected_result = 0x1

        for func_name, func in self.__dec_funcs.items():
            self.clear_negative_flag()
            self.memory.set_address(self.__memory_address_to_decrement, 0xFF)
            func()
            actual_result = self.get_negative_flag()
            self.assertEqual(expected_result,
                             actual_result,
                             "Incorrect negative flag after executing {fn}. Expeced {ex} but got {ar}."
                             .format(fn=func_name, ex=expected_result, ar=actual_result))

    def test_dec_sets_zero_flag(self):
        expected_result = 0x1

        for func_name, func in self.__dec_funcs.items():
            self.clear_zero_flag()
            self.memory.set_address(self.__memory_address_to_decrement, 0x1)
            func()
            actual_result = self.get_zero_flag()
            self.assertEqual(expected_result,
                             actual_result,
                             "Incorrect zero flag after executing {fn}. Expeced {ex} but got {ar}."
                             .format(fn=func_name, ex=expected_result, ar=actual_result))

    def __do_dec_immediate(self):
        self.target.dec_immediate(self.__memory_address_to_decrement)

    def __do_dec_absolute(self):
        self.prepare_absolute_operation(self.__memory_address_to_decrement)
        self.target.dec_absolute(0x03)

    def __do_dec_absolute_indexed(self):
        self.prepare_absolute_indexed_operation(self.__memory_address_to_decrement)
        self.target.dec_absolute_indexed(0x02, 'X')

    def __do_dec_indexed_indirect(self):
        self.prepare_indexed_indirect_operation(self.__memory_address_to_decrement)
        self.target.dec_indexed_indirect(0x03)

    def __do_dec_indirect_indexed(self):
        self.prepare_indirect_indexed_operation(self.__memory_address_to_decrement)
        self.target.dec_indirect_indexed(0x03)
