import unittest

import Chip6502 as chip
import NesMemory as memory
import Tests.Util.Register as register

class TestChip6502(unittest.TestCase):

    def setUp(self):
        self.__memory = memory.NesMemory(0xFFFF)
        self.__target = chip.Chip6502(self.__memory)
        self.__registers = ['accumulator', 'x_register', 'y_register']

        self.__get_accumulator = register.get_accumulator_func(self.__target)
        self.__set_accumulator = register.set_accumulator_func(self.__target)
        self.__get_x_register = register.get_x_register_func(self.__target)
        self.__set_x_register = register.set_x_register_func(self.__target)
        self.__get_y_register = register.get_y_register_func(self.__target)
        self.__set_y_register = register.set_y_register_func(self.__target)

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
            self.assertEqual(flag_end,
                             getattr(self.__target, flag_name),
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

    def test_load_immediate_registers(self):
        """
        Test that loading a register using immediate addressing loads the value provided into the register

        E.g. LDA 0x01 causes 0x01 to be loaded into the accumulator
        """
        def assert_load_immediate_register(target_func, get_register_func):
            value = 0x01
            target_func(value)
            result = get_register_func()
            self.assertEqual(value,
                             result,
                             "Failed while executing {func}. Expected {expected}. Got {result}."
                             .format(func=target_func, expected=hex(value), result=hex(result)))

        mappings = {
            self.__target.lda_immediate: self.__get_accumulator,
            self.__target.ldx_immediate: self.__get_x_register,
            self.__target.ldy_immediate: self.__get_y_register
        }

        for f, get_func in mappings.items():
            assert_load_immediate_register(f, get_func)


    def test_store_immediate_or_absolute_registers(self):
        """
        Test that storing a register using immediate or absolute addressing stores register into the memory address
        provided

        E.g. STA 0x01 causes the accumulator to be stored to memory location 0x01

        Seems a bit silly having two addressing methods doing the same thing -- either I misunderstand how this operates
        or one of these isn't actually valid. My guess: immediate is inappropriate for use with register storage.
        """
        def assert_store_immediate_register(target_func, set_register_func):
            register_value=0xFF
            target_address = 0x12

            set_register_func(register_value)
            target_func(target_address)

            result = self.__memory.get_address(target_address)

            self.assertEqual(register_value,
                             result,
                             "Expected {target_address} to be {register_value} when calling {func}. It was {result}."
                             .format(target_address=hex(target_address),
                                     register_value=hex(register_value),
                                     func=target_func,
                                     result=hex(result))
            )

        target_funcs = {
            self.__target.sta_immediate: self.__set_accumulator,
            self.__target.stx_immediate: self.__set_x_register,
            self.__target.sty_immediate: self.__set_y_register,
            self.__target.sta_absolute: self.__set_accumulator,
            self.__target.stx_absolute: self.__set_x_register,
            self.__target.sty_absolute: self.__set_y_register
        }

        for target_func, set_register_func in target_funcs.items():
            assert_store_immediate_register(target_func, set_register_func)

    def test_load_absolute_register(self):
        """
        Test that loading a register using absolute addressing loads the value stored at a memory location into the
        register

        E.g. LDA $0x01, when 0x0D is stored at 0x01 causes 0x01 to be loaded into the accumulator
        """
        def assert_load_absolute_register(target_func, get_register_func):
            expected_value = 0x0D
            memory_address = 0x01
            self.__memory.set_address(memory_address, expected_value)

            target_func(memory_address)
            self.assertEqual(expected_value,
                             get_register_func(),
                             "Failed while executing {func}. Expected {expected}. Got {result}"
                             .format(func=target_func, expected=expected_value, result=get_register_func()))

        test_mappings = {
            self.__target.lda_absolute: self.__get_accumulator,
            self.__target.ldx_absolute: self.__get_x_register,
            self.__target.ldy_absolute: self.__get_y_register
        }

        for target_func, get_register_func in test_mappings.items():
            assert_load_absolute_register(target_func, get_register_func)

    def test_load_absolute_indexed_register(self):
        """
        Assert that loading a register using absolute indexed addressing causes the register to be loaded from a memory
        address that is the one given plus the value of the given register.

        E.g. LDA $0001k,X when x-register=3 causes the accumulator to be loaded from addres $0004
        """
        base_address = 0x0001
        address_offset = 0x0003
        memory_data = 0x0D

        set_register_mappings = {'X': self.__set_x_register,
                                 'Y': self.__set_y_register}

        test_mappings = {
            self.__target.lda_absolute_indexed: self.__get_accumulator,
            self.__target.ldx_absolute_indexed: self.__get_x_register,
            self.__target.ldy_absolute_indexed: self.__get_y_register
        }

        self.__memory.set_address(base_address + address_offset, memory_data)
        fail_msg = "Failed while executing {func} for {register_letter}. Expected {memory_data}. Got {result}."

        for target_func, get_register_func in test_mappings.items():

            for register_letter, set_register_func in set_register_mappings.items():

                set_register_func(address_offset)
                target_func(base_address, register_letter)
                result = get_register_func()

                self.assertEqual(memory_data,
                                 get_register_func(),
                                 (fail_msg.format(func=target_func,
                                                  register_letter=register_letter,
                                                  memory_data=hex(memory_data),
                                                  result=hex(result))))

    def test_load_register_indexed_indirect(self):
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
        def assert_load_register_indexed_indirect(get_register_func, target_func):
            self.__target.x_register = 0x03
            self.__memory.set_address(0x0F, 0x11)
            self.__memory.set_address(0x10, 0xFF)
            self.__memory.set_address(0xFF11, 0x37)
            target_func(0x0C)
            self.assertEqual(0x37, get_register_func())

        mappings = {
            self.__get_accumulator: self.__target.lda_indexed_indirect,
            self.__get_x_register: self.__target.ldx_indexed_indirect,
            self.__get_y_register: self.__target.ldy_indexed_indirect
        }

        for k,v in mappings.items():
            assert_load_register_indexed_indirect(k, v)

    def test_store_register_indexed_indirect(self):
        """
        Indexed indirect addressing is done by taking the given address and adding the contents of the X register.

        This gives a new address. Load that and the next address along and combine them into a little-endian number to
        get another address. Load the contents of that address into the register.

        E.g. LDA $000C,X when x-register is 3 gives us a new address:

        0x000F

        0x000F contains 0x11. 0x0010 contains 0xFF. This give us a little-endian number that is the final address to visit:

        0xFF11, which contains 0x37.

        So 0x37 is the value to be loaded in to the accumulator.
        """
        def assert_store_register_indexed_indirect(set_register_func, target_func):
            self.__target.x_register = 0x03
            set_register_func(0x37)
            self.__memory.set_address(0x0F, 0x11)
            self.__memory.set_address(0x10, 0xFF) # so target address is 0xFF11
            target_func(0x0C)
            self.assertEqual(0x37, self.__memory.get_address(0xFF11))

        mappings = {
            self.__set_accumulator: self.__target.sta_indexed_indirect,
            self.__set_y_register: self.__target.sty_indexed_indirect
        }

        for k,v in mappings.items():
            assert_store_register_indexed_indirect(k, v)

    def test_load_register_indirect_indexed(self):
        """
        Indirect indexed addressing is done by taking the address given and the one after it and using the values to
        make a new 16-bit address. Add the value of the Y-register to that address and load the value that is at the
        final address.

        e.g. LDA(0x02),Y where:

           * 0x02 contains 0x01
           * 0x03 contains 0x12
           * The Y-register contains 0x02

        Then combine 0x02 and 0x03 to make a little-endian address:

        0x01 + 0x12 = 0x1201

        Then add the contents of the Y-register:

        0x1201 + 0x02 = 0x1203

        Supposing 0x1203 contains 0xFE then load 0xFE into the accumulator.
        """
        def assert_load_register_indirect_indexed(target_func, get_register_func):
            self.__target.y_register = 0x02
            self.__memory.set_address(0x02, 0x01)
            self.__memory.set_address(0x03, 0x12)
            self.__memory.set_address(0x1203, 0xFE)
            target_func(0x02)
            self.assertEqual(0xFE, get_register_func())

        mappings = {
            self.__target.lda_indirect_indexed: self.__get_accumulator,
            self.__target.ldx_indirect_indexed: self.__get_x_register,
            self.__target.ldy_indirect_indexed: self.__get_y_register
        }

        for k, v in mappings.items():
            assert_load_register_indirect_indexed(k, v)

    def test_store_register_indirect_indexed(self):
        """
        Indexed indirect addressing is done by taking the given address and adding the contents of the X register.

        This gives a new address. Load that and the next address along and combine them into a little-endian number to
        get another address. Load the contents of that address into the register.

        E.g. LDA $000C,X when x-register is 3 gives us a new address:

        0x000F

        0x000F contains 0x11. 0x0010 contains 0xFF. This give us a little-endian number that is the final address to visit:

        0xFF11, which contains 0x37.

        So 0x37 is the value to be loaded in to the accumulator.
        """
        def assert_store_register_indirect_indexed(target_func, set_register_func):
            self.__target.y_register = 0x02
            set_register_func(0x11)
            self.__memory.set_address(0x02, 0x01)
            self.__memory.set_address(0x03, 0x12) # target address: 0x1203
            target_func(0x02)
            self.assertEqual(0x11, self.__memory.get_address(0x1203))

        mappings = {
            self.__target.sta_indirect_indexed: self.__set_accumulator,
            self.__target.stx_indirect_indexed: self.__set_x_register
        }

        for k, v in mappings.items():
            assert_store_register_indirect_indexed(k, v)

    def test_clc(self):
        """
        Test that when the CLC instruction is issued, the carry flag is set to zero.
        """
        self.__assert_carry_flag(self.__target.clc, 0x0)

    def test_sec(self):
        """
        Test that when the SEC instruction is issued, the carry flag is set to 1.
        """
        self.__assert_carry_flag(self.__target.sec, 0x1)

    def __assert_carry_flag(self, carry_flag_init_func, expected_value):
        values = [0x0, 0x1]
        for v in values:
            self.__target.carry_flag = v
            carry_flag_init_func()
            self.assertEqual(expected_value,
                            self.__target.carry_flag,
                            """Carry flag not expected value of {ex} from starting state of {state}.
                            Instead it was {val}""".format(state=v, ex=expected_value, val=self.__target.carry_flag))   
