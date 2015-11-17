import Tests.Chip6502.IncrementDecrement.IncDecBaseTest as base_test

class TestInc(base_test.IncDecBaseTest):


    def setUp(self):
        super().setUp()

        self.inc_dec_funcs = {'inc_immediate': self.__do_inc_immediate,
                             'inc_absolute': self.__do_inc_absolute,
                             'inc_absolute_indexed': self.__do_inc_absolute_indexed,
                             'inc_indexed_indirect': self.__do_inc_indexed_indirect,
                             'inc_indirect_indexed': self.__do_inc_indirect_indexed
                     }
        self.__init_memory = lambda: self.memory.set_address(self.__memory_address_to_increment, 0x01)

        self.__memory_address_to_increment = 0x01
        self.__init_memory

    def test_inc_increments_memory_value(self):
        expected_result = 0x02

        self.assert_inc_dec_decrements_memory_value(expected_result,
                                                    self.__init_memory,
                                                    self.__memory_address_to_increment)

    def test_inc_sets_negative_flag(self):
        self.assert_inc_dec_sets_negative_flag(0x7F, self.__memory_address_to_increment)

    def __do_inc_immediate(self):
        self.target.inc_immediate(self.__memory_address_to_increment)

    def __do_inc_absolute(self):
        self.prepare_absolute_operation(self.__memory_address_to_increment)
        self.target.inc_absolute(0x03)

    def __do_inc_absolute_indexed(self):
        self.prepare_absolute_indexed_operation(self.__memory_address_to_increment)
        self.target.inc_absolute_indexed(0x02, 'X')

    def __do_inc_indexed_indirect(self):
        self.prepare_indexed_indirect_operation(self.__memory_address_to_increment)
        self.target.inc_indexed_indirect(0x03)

    def __do_inc_indirect_indexed(self):
        self.prepare_indirect_indexed_operation(self.__memory_address_to_increment)
        self.target.inc_indirect_indexed(0x03)
