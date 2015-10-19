import unittest

import Chip6502 as chip
import NesMemory as memory


class TestChip6502(unittest.TestCase):

    def setUp(self):
        self.__memory = memory.NesMemory(0xFFFF)
        self.__target = chip.Chip6502(self.__memory)
        self.__registers = ['accumulator', 'x_register', 'y_register']

    def test_instantiation_zeroes_internal_state(self):
        """
        When the chip is first powered on it should set a bunch of internal state to zero.

        See state_fields for the list of things internal to the processor that should be zeroed.
        """
        target = chip.Chip6502(self.__memory)

        state_fields = ['accumulator',
                        'carry_flag',
                        'overflow_flag',
                        'zero_flag',
                        'negative_flag',
                        'x_register',
                        'y_register']

        for sf in state_fields:
            result = getattr(target, sf)
            self.assertEqual(0x0, result,
                             "Expected {field} to be 0x0. Instead it was {result}.".format(field=sf, result=result))

    def test_setting_register_to_zero_sets_zero_flag(self):
        self.__assert_setting_register_affects_zero_flag(0x00, 0x00, 0x01)

    def test_setting_register_to_non_zero_clears_the_zero_flag(self):
        self.__assert_setting_register_affects_zero_flag(0x01, 0x01, 0x00)

    def __assert_setting_register_affects_zero_flag(self, zero_flag_start, register_value, zero_flag_end):
        """
        Assert that settting registers causes the zero flag to react appropriately.

        The zero flag should be set if register_Value is 0. Otherwise it should be cleared.
        """
        self.__assert_setting_register_affects_flag("zero_flag", zero_flag_start, register_value, zero_flag_end)

    def test_setting_register_sets_negative_flag_if_bit_seven_is_set(self):
        """
        registers hold an eight-bit signed number. If bit seven (128) is set to 1 then the chip should set its
        negative flag.
        """
        self.__assert_setting_register_affects_negative_flag(0x00, 0xFF, 0x01)

    def test_setting_accumulator_clears_negative_flag_if_seventh_bit_is_not_set(self):
        self.__assert_setting_register_affects_negative_flag(0x01, 0x01, 0x00)

    def __assert_setting_register_affects_negative_flag(self, flag_start, register_value, flag_end):
        """
        Assert that settting registers causes the negative flag to react appropriately.

        The negative flag should be set if bit seven of register_Value is 1. Otherwise it should be cleared.
        """
        self.__assert_setting_register_affects_flag("negative_flag", flag_start, register_value, flag_end)

    def __assert_setting_register_affects_flag(self, flag_name, flag_start, register_value, flag_end):
        """
        Assert that that setting registers to a given value causes the given flag to go from one state to another.

        An assertEqual call is made to ensure that the flag ends up with the value of flag_end.

        See the setUp method for the list of registers.

        Args:
            flag_name: The name of the flag that is affected
            flag_start: The initial value of the flag before the register set operation
            register_value: The value to set the register to
            flag_end: The expected end state of the flag
        """
        for r in self.__registers:
            setattr(self.__target, flag_name, flag_start)
            setattr(self.__target, r, register_value)
            self.assertEqual(flag_end, getattr(self.__target, flag_name),
                             "Expected {flag_name} to be {value} when {register} was set to {regval}. It wasn't".
                             format(flag_name=flag_name, value=flag_end, register=r, regval=register_value))

    def test_overflowing_register_raises_register_overflow_exception(self):
        """
        When a register contains a value > 0xFF, it will overflow, causing a register overflow exception
        """
        for r in self.__registers:
            def overflow_register():
                setattr(self.__target, r, 0x100)

            self.assertRaises(chip.RegisterOverflowException, overflow_register)

    def test_load_immediate_register(self):
        """
        Test that loading a register using immediate addressing loads the value provided into the register

        E.g. LDA 0x01 causes 0x01 to be loaded into the accumulator
        """
        mappings = {self.__target.lda_immediate: lambda: self.__target.accumulator,
                    self.__target.ldx_immediate: lambda: self.__target.x_register,
                    self.__target.ldy_immediate: lambda: self.__target.y_register}
        value = 0x01

        for f, get_func in mappings.items():
            f(value)
            result = get_func()
            self.assertEqual(value,
                             result,
                             "Failed while executing {func}. Expected {expected}. Got {result}."
                             .format(func=f, expected=hex(value), result=hex(result)))

    def test_load_absolute_register(self):
        """
        Test that loading a register using absolute addressing loads the value stored at a memory location into the
        register

        E.g. LDA $0x01, when 0x0D is stored at 0x01 causes 0x01 to be loaded into the accumulator
        """
        expected_value = 0x0D
        memory_address = 0x01
        self.__memory.set_address(memory_address, expected_value)

        test_mappings = {self.__target.lda_absolute: lambda: self.__target.accumulator,
                         self.__target.ldx_absolute: lambda: self.__target.x_register,
                         self.__target.ldy_absolute: lambda: self.__target.y_register}

        for target_func, get_register_func in test_mappings.items():
            target_func(memory_address)
            self.assertEqual(expected_value,
                             get_register_func(),
                             "Failed while executing {func}. Expected {expected}. Got {result}"
                             .format(func=target_func, expected=expected_value, result=get_register_func()))

    def test_load_absolute_indexed_register(self):
        """
        Assert that loading a register using absolute indexed addressing causes the register to be loaded from a memory
        address that is the one given plus the value of the given register.

        E.g. LDA $0001k,X when x-register=3 causes the accumulator to be loaded from addres $0004
        """
        base_address = 0x0001
        address_offset = 0x0003
        memory_data = 0x0D

        def set_x_register(val):
            self.__target.x_register = val

        def set_y_register(val):
            self.__target.y_register = val

        set_register_mappings = {'X': set_x_register,
                                 'Y': set_y_register}

        test_mappings = {self.__target.ldx_absolute_indexed : lambda: self.__target.x_register,
                         self.__target.lda_absolute_indexed: lambda: self.__target.accumulator,
                         self.__target.ldy_absolute_indexed: lambda: self.__target.y_register}

        for target_func, get_register_func in test_mappings.items():
            for register_letter, set_register_func in set_register_mappings.items():
                set_register_func(address_offset)
                self.__memory.set_address(base_address + address_offset, memory_data)
                target_func(base_address, register_letter)
                result = get_register_func()
                fail_msg = "Failed while executing {func} for {register_letter}. Expected {memory_data}. Got {result}."
                self.assertEqual(memory_data,
                                 get_register_func(),
                                 (fail_msg.format(func=target_func,
                                                  register_letter=register_letter,
                                                  memory_data=hex(memory_data),
                                                  result=hex(result))))

    def test_load_register_indexed_indirect(self):
        mappings = {
        lambda: self.__target.accumulator: self.__target.lda_indexed_indirect,
        lambda: self.__target.x_register: self.__target.ldx_indexed_indirect,
        lambda: self.__target.y_register: self.__target.ldy_indexed_indirect
        }

        for k,v in mappings.items():
            self.__assert_load_register_indexed_indirect(k, v)

    def __assert_load_register_indexed_indirect(self, get_register_func, target_func):
        """
        Indexed indirect addressing is done by taking the given address and adding the contents of the X register.

        This gives a new address. Load that and the next address along and combine them into a little-endian number to
        get another address. Load the contents of that address into the register.

        E.g. LDA $000C,X when x-register is 3 gives us a new address:

        0x000F

        0x000F contains 0x11. 0x0010 contains 0xFF.

        This give us a little-endian number that is the final address to visit:

        0xFF11, which contains 0x37.

        So 0x37 is the value to be loaded in to the accumulator.
        """
        self.__target.x_register = 0x03
        self.__memory.set_address(0x0F, 0x11)
        self.__memory.set_address(0x10, 0xFF)
        self.__memory.set_address(0xFF11, 0x37)
        target_func(0x0C)
        self.assertEqual(0x37, get_register_func())
