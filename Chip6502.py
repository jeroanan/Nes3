class Chip6502(object):

    def __init__(self, memory):
        """
        Initialise the state of the chip
        """
        self.__accumulator = 0x0
        self.carry_flag = 0x0
        self.overflow_flag = 0x0
        self.zero_flag = 0x0
        self.negative_flag = 0x0
        self.__x_register = 0x0
        self.__y_register = 0x0
        self.__ram = memory

        self.lda_immediate = lambda val: self.__load_register_immediate(val, self.__set_accumulator)
        self.ldx_immediate = lambda val: self.__load_register_immediate(val, self.__set_x_register)
        self.ldy_immediate = lambda val: self.__load_register_immediate(val, self.__set_y_register)

        # See my unit test for sta_immediate_or_absolute: either I misunderstand or one of these two doesn't exist.
        self.sta_immediate = lambda addr: self.__store_register_immediate(addr, self.__get_accumulator)
        self.stx_immediate = lambda addr: self.__store_register_immediate(addr, self.__get_x_register)
        self.sty_immediate = lambda addr: self.__store_register_immediate(addr, self.__get_y_register)

        self.lda_absolute = lambda addr: self.__load_register_absolute(addr, self.__set_accumulator)
        self.ldx_absolute = lambda addr: self.__load_register_absolute(addr, self.__set_x_register)
        self.ldy_absolute = lambda addr: self.__load_register_absolute(addr, self.__set_y_register)

        self.sta_absolute = lambda addr: self.__store_register_immediate(addr, self.__get_accumulator)
        self.stx_absolute = lambda addr: self.__store_register_immediate(addr, self.__get_x_register)
        self.sty_absolute = lambda addr: self.__store_register_immediate(addr, self.__get_y_register)

        self.ldx_indexed_indirect = lambda addr: self.__load_indexed_indirect_register(addr, self.__set_x_register)
        self.ldy_indexed_indirect = lambda addr: self.__load_indexed_indirect_register(addr, self.__set_y_register)
        self.lda_indexed_indirect = lambda addr: self.__load_indexed_indirect_register(addr, self.__set_accumulator)

        self.sta_indexed_indirect = lambda addr: self.__store_indexed_indirect_register(addr, self.__get_accumulator)
        self.sty_indexed_indirect = lambda addr: self.__store_indexed_indirect_register(addr, self.__get_y_register)

        self.lda_indirect_indexed = lambda addr: self.__load_indirect_indexed_register(addr, self.__set_accumulator)
        self.ldx_indirect_indexed = lambda addr: self.__load_indirect_indexed_register(addr, self.__set_x_register)
        self.ldy_indirect_indexed = lambda addr: self.__load_indirect_indexed_register(addr, self.__set_y_register)

        self.sta_indirect_indexed = lambda addr: self.__store_indirect_indexed_register(addr, self.__get_accumulator)
        self.stx_indirect_indexed = lambda addr: self.__store_indirect_indexed_register(addr, self.__get_x_register)

        self.__get_accumulator = lambda: self.accumulator
        self.__get_x_register = lambda: self.x_register
        self.__get_y_register = lambda: self.y_register

        self.adc_absolute = lambda address: self.__add_to_accumulator(self.__ram.get_address(address))
        self.adc_immediate = lambda operand: self.__add_to_accumulator(operand)
        self.adc_indexed_indirect = lambda addr: self.__add_to_accumulator(
            self.__ram.get_address(self.__ram.get_indexed_indirect_memory_address(addr, self.__get_x_register())))
        self.adc_indirect_indexed = lambda addr: self.__add_to_accumulator(
            self.__ram.get_address(self.__ram.get_indirect_indexed_memory_address(addr, self.__get_y_register())))

        self.sbc_immediate = lambda operand: self.__subtract_from_accumulator(operand)
        self.sbc_absolute = lambda addr: self.__subtract_from_accumulator(self.__ram.get_address(addr))
        self.sbc_indexed_indirect = lambda addr: self.__subtract_from_accumulator(
            self.__ram.get_address(self.__ram.get_indexed_indirect_memory_address(addr, self.__get_x_register())))
        self.sbc_indirect_indexed = lambda addr: self.__subtract_from_accumulator(
            self.__ram.get_address(self.__ram.get_indirect_indexed_memory_address(addr, self.__get_y_register())))

        self.inc_immediate = lambda address: self.__increment_memory_value(address)

    @property
    def accumulator(self):
        """
        The accumulator keeps track of what's going on in the chip

        Returns:
               The current value of the accumulator
        """
        return self.__accumulator

    @accumulator.setter
    def accumulator(self, val):
        """
        Set the accumulator.

        Register setters call self.__set_register in order to set their values. This is so processor status flags can
        be set based on the new value.
        """

        def set_register():
            self.__accumulator = val

        self.__set_register(val, set_register)

    # We have private get/set functions in addition to the property getter/setters.
    # These are used as parameters to the set/load register functions.
    def __set_accumulator(self, val):
        self.accumulator = val

    @property
    def x_register(self):
        """
        The X register is a general data-storage register.

        Returns:
               The current value of the X register
        """
        return self.__x_register

    @x_register.setter
    def x_register(self, val):
        # set the x-register

        def set_register():
            self.__x_register = val

        self.__set_register(val, set_register)

    def __set_x_register(self, val):
        self.x_register = val

    @property
    def y_register(self):
        """
        The Y register is a general data-storage register.

        Returns:
               The current value of the Y register
        """
        return self.__y_register

    @y_register.setter
    def y_register(self, val):
        #Set the y-register

        def set_register():
            self.__y_register = val

        self.__set_register(val, set_register)

    def __set_y_register(self, val):
        self.y_register = val

    def __set_register(self, val, set_reg_func):
        """
        Set a register.

        The following status flags are set as a result of this operation:

            * zero_flag is set if val is zero -- it is cleared otherwise.
            * negative_flag if the seventh bit of val is 1

        Args:
            val: The value to set the register to
            set_reg_func: A function that sets the register. It should close off its value as this method
                          won't provide it.

        Raises:
            RegisterOverflowException: val is longer than two bytes (0xFF)
        """
        def check_overflow():
            if val > 0xFF:
                raise RegisterOverflowException

        def set_zero_flag():
            if val == 0x0:
                self.zero_flag = 0x01
            else:
                self.zero_flag = 0x00

        def set_negative_flag():
            if val & 0xFF == 0xFF:
                self.negative_flag = 0x01
            else:
                self.negative_flag = 0x00

        check_overflow()
        set_reg_func()
        set_zero_flag()
        set_negative_flag()

    def __load_register_immediate(self, value, set_register_func):
        """
        Loading a register using immediate addressing loads the register with the value given.

        E.g. LDA 0x01 loads the value 0x01 into the accumulator

        Args:
            value: The value to load into the register
            set_register_func: A function to use to set the value of the register
        """
        set_register_func(value)

    def __store_register_immediate(self, address, get_register_func):
        """
        Storing a register using immediate addressing stores the value of the register into the memory address provided

        E.g. STA 0x01 causes the accumulator to be stored to memory location 0x01

        Args:
            address: The memory address to store the contents of the register to
            get_register_func: A function by which the contents of the register can be retrieved
        """
        self.__ram.set_address(address, get_register_func())

    def __load_register_absolute(self, address, set_register_func):
        """
        Loading a register using absolute addressing stores the value at the memory address specified into the register

        Args:
            address: The memory address whose value is to be loaded into the register
            set_register_func: A function to use to set the value of the register
        """
        set_register_func(self.__ram.get_address(address))

    def lda_absolute_indexed(self, address, register):
        self.__load_absolute_indexed_register(address, register, self.__set_accumulator)

    def ldx_absolute_indexed(self, address, register):
        self.__load_absolute_indexed_register(address, register, self.__set_x_register)

    def ldy_absolute_indexed(self, address, register):
        self.__load_absolute_indexed_register(address, register, self.__set_y_register)

    def __load_absolute_indexed_register(self, address, register, set_register_func):
        offset_function = self.__get_y_register
        if register == "X":
            offset_function = self.__get_x_register

        address_to_load = self.__ram.get_absolute_indexed_address(address, offset_function)
        set_register_func(self.__ram.get_address(address_to_load))

    def __load_indexed_indirect_register(self, address, set_register_func):
        addr = self.__ram.get_indexed_indirect_memory_address(address, self.x_register)
        set_register_func(self.__ram.get_address(addr))

    def __store_indexed_indirect_register(self, address, get_register_func):
        addr = self.__ram.get_indexed_indirect_memory_address(address, self.x_register)
        self.__ram.set_address(addr, get_register_func())

    def __load_indirect_indexed_register(self, address, set_register_func):
        addr = self.__ram.get_indirect_indexed_memory_address(address, self.y_register)
        set_register_func(self.__ram.get_address(addr))

    def __store_indirect_indexed_register(self, address, get_register_func):
        addr = self.__ram.get_indirect_indexed_memory_address(address, self.y_register)
        self.__ram.set_address(addr, get_register_func())

    def __combine_two_consecutive_address_values(self, first_address):

        def get_two_consecutive_address_values(first_address):
            return (self.__ram.get_address(first_address), self.__ram.get_address(first_address+0x01))

        def combine_two_hex_addresses(address1, address2):
            """
            Combine two 8-bit hex numbers into a 16 bit little-endian hex number

            e.g: self.__combine_two_hex_addresses(0x02, 0x22) gives 0x2202

            Args:
                address1: The first hex number
                address2: The second hex number

            Returns:
                The two numbers combined into a 16-bit number as described above
            """
            get_hex_digits = lambda hex_value: str(hex_value).split('x')[1].zfill(2)

            hex_address = "0x{first_digit}{second_digit}".format(first_digit=get_hex_digits(hex(address2)),
                                                                second_digit=get_hex_digits(hex(address1)))
            return int(hex_address, 0)

        contents1, contents2 = get_two_consecutive_address_values(first_address)
        return combine_two_hex_addresses(contents1, contents2)

    def clc(self):
        """
        Clear the carry flag

        Causes the carry flag to become 0x0 no matter what its current value is.

        Addressing modes: Implied addressing only.
        """
        self.carry_flag = 0x0

    def sec(self):
        """
        Set the carry flag.

        Causes the carry flag to become 0x1 no matter what its current value is.

        Addressing modes: Implied addressing only.
        """
        self.carry_flag = 0x1

    def adc_absolute_indexed(self, address, register):
        get_register_func = self.__get_register_func_from_register_letter(register)
        self.__add_to_accumulator(self.__ram.get_address(address + get_register_func()))

    def sbc_absolute_indexed(self, address, register):
        get_register_func = self.__get_register_func_from_register_letter(register)
        self.__subtract_from_accumulator(self.__ram.get_address(address + get_register_func()))

    def __get_register_func_from_register_letter(self, register_letter):
        get_register_func = self.__get_y_register

        if register_letter == 'X':
            get_register_func = self.__get_x_register

        return get_register_func

    def __add_to_accumulator(self, operand):
        arithmetic_func = lambda: self.__accumulator + operand + self.carry_flag

        def carry_flag_func(sum_value):
            if sum_value > 0xFF:
                self.carry_flag = 0x01
            else:
                self.carry_flag = 0x00

        self.__perform_accumulator_arithmetic(arithmetic_func, carry_flag_func)

    def __subtract_from_accumulator(self, operand):
        arithmetic_func = lambda: self.__get_accumulator() - operand - (1 - self.carry_flag)

        def carry_flag_func(sum_value):
            if sum_value >= 0:
                self.carry_flag = 0x01
            else:
                self.carry_flag = 0x0

        self.__perform_accumulator_arithmetic(arithmetic_func, carry_flag_func)

    def __perform_accumulator_arithmetic(self, arithmetic_func, carry_flag_func):
        the_sum = arithmetic_func()

        carry_flag_func(the_sum)
        the_sum = min(0xFF, the_sum)

        accumulator_seventh_bit = 0x80 & self.__get_accumulator()
        result_seventh_bit = 0x80 & the_sum

        if accumulator_seventh_bit != result_seventh_bit:
            self.overflow_flag = 0x01
        else:
            self.overflow_flag = 0x00

        self.__set_accumulator(the_sum)



    def __increment_memory_value(self, address):
        address_value = self.__ram.get_address(address)
        self.__ram.set_address(address, address_value + 0x01)

class RegisterOverflowException(Exception):
    pass
