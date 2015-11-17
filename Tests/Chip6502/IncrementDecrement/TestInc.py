import Tests.Chip6502.BaseTest as base_test

class TestInc(base_test.BaseTest):

    def setUp(self):
        super().setUp()

    def test_inc_increments_memory_value(self):
        memory_address = 0x01
        starting_value = 0x02
        expected_result = 0x03

        inc_funcs = {'inc_immediate': self.target.inc_immediate}

        for func_name, func in inc_funcs.items():
            self.memory.set_address(memory_address, starting_value)
            func(memory_address)
            actual_result = self.memory.get_address(memory_address)
            self.assertEqual(expected_result,
                             actual_result,
                             "Incorrect memory value retrieved when executing {fn}. Expected {ex} but got {ar}."
                             .format(fn=func_name, ex=expected_result, ar=actual_result))
