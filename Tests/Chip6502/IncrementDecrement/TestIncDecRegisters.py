import Tests.Chip6502.BaseTest as base_test

class TestIncDecRegisters(base_test.BaseTest):

    def setUp(self):
        super().setUp()

        self.__funcs = {'': ''}

    def test_inc_dec_x_register(self):
        self.__funcs = {'inc_x_register': (self.target.inc_x_register, 0x03),
                        'dec_x_register': (self.target.dec_x_register, 0x01)}

        self.__assert_inc_dec_register(self.set_x_register, self.get_x_register)        

    def test_inc_dec_y_register(self):
        self.__funcs = {'inc_y_register': (self.target.inc_y_register, 0x03),
                        'dec_y_register': (self.target.dec_y_register, 0x01)}

        self.__assert_inc_dec_register(self.set_y_register, self.get_y_register)

    def __assert_inc_dec_register(self, set_register_func, get_register_func):
         for func_name, func_with_expected_result in self.__funcs.items():
             set_register_func(0x02)
             func, expected_value = func_with_expected_result
             func()
             actual_value = get_register_func()
             self.assertEqual(expected_value,
                              actual_value,
                              "Incorrect register value while executing {fn}. Expected {ex}. Got {av}."
                              .format(fn=func_name, ex=expected_value, av=actual_value))
