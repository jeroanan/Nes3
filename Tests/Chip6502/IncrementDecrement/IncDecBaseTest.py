import Tests.Chip6502.BaseTest as base_test

class IncDecBaseTest(base_test.BaseTest):

    def setUp(self):
        super().setUp()

        self.inc_dec_funcs = {'':''}

    def assert_inc_dec_decrements_memory_value(self, expected_result, init_memory_func, inc_dec_address):

        for func_name, func in self.inc_dec_funcs.items():
            init_memory_func()
            func()
            actual_result = self.memory.get_address(inc_dec_address)
            self.assertEqual(expected_result,
                             actual_result,
                             "Incorrect memory value retrieved when executing {fn}. Expected {ex} but got {ar}."
                             .format(fn=func_name, ex=expected_result, ar=actual_result))

    def assert_inc_dec_sets_negative_flag(self, starting_address_value, inc_dec_address):
        expected_result = 0x1

        for func_name, func in self.inc_dec_funcs.items():
            self.clear_negative_flag()
            self.memory.set_address(inc_dec_address, starting_address_value)
            func()
            actual_result = self.get_negative_flag()
            self.assertEqual(expected_result,
                             actual_result,
                             "Incorrect negative flag after executing {fn}. Expeced {ex} but got {ar}."
                             .format(fn=func_name, ex=expected_result, ar=actual_result))
