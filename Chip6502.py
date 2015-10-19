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
        The accumulator keeps track of what's going on in the chip
        """
        def set_register():
            self.__accumulator = val

        self.__set_register(val, set_register)

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
        """
        The X register is a general data-storage register.
        """
        def set_register():
            self.__x_register = val

        self.__set_register(val, set_register)

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
        """
        The Y register is a general data-storage register.
        """
        def set_register():
            self.__y_register = val

        self.__set_register(val, set_register)

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
            if val & 255 == 255:
                self.negative_flag = 0x01
            else:
                self.negative_flag = 0x00

        check_overflow()
        set_reg_func()
        set_zero_flag()
        set_negative_flag()

    def lda_immediate(self, value):
        """
        The LDA immediate instruction loads the accumulator with the value supplied.

        Args:
            value: The value to load into the accumulator
        """
        self.accumulator = value

    def lda_absolute(self, address):
        """
        The LDA absolute instruction stores that value of the memory address specified in address into the accumulator

        Args:
            address: The memory address whose value is to be loaded into the accumulator
        """
        self.accumulator = self.__ram.get_address(address)

    def lda_absolute_indexed(self, address, register):
        def set_accumulator(val):
            self.accumulator = val

        self.__load_absolute_indexed_register(address, register, set_accumulator)

    def lda_indexed_indirect(self, address):
        def set_register(val):
            self.accumulator = val

        self.__load_indexed_indirect_register(address, set_register)

    def ldx_immediate(self, value):
        """
        The LDX immediate instruction loads the X register with the value supplied.

        Args:
            value: The value to loads into the X register
        """
        self.x_register = value

    def ldx_absolute(self, address):
        """
        The LDX absolute instruction stores that value of the memory address specified in address into the x register

        Args:
            address: The memory address whose value is to be loaded into the x register
        """
        self.x_register = self.__ram.get_address(address)

    def ldx_absolute_indexed(self, address, register):
        def set_x_register(val):
            self.x_register = val

        self.__load_absolute_indexed_register(address, register, set_x_register)

    def ldx_indexed_indirect(self, address):

        def set_register(val):
            self.x_register = val

        self.__load_indexed_indirect_register(address, set_register)

    def ldy_immediate(self, value):
        """
        The LDY immediate instruction loads the Y register with the value supplied.

        Args:
            value: The value to loads into the Y register
        """
        self.y_register = value

    def ldy_absolute(self, address):
        """
        The LDY absolute instruction stores that value of the memory address specified in address into the y register

        Args:
            address: The memory address whose value is to be loaded into the y register
        """
        self.y_register = self.__ram.get_address(address)

    def ldy_absolute_indexed(self, address, register):
        def set_y_register(val):
            self.y_register = val

        self.__load_absolute_indexed_register(address, register, set_y_register)

    def __load_absolute_indexed_register(self, address, register, set_register_func):
        """
        Load data into a register. The data is located in the given address plus the value held in a given register.

        e.g. If address given is 0x01 and the X-register contains 0x04, then the following call:

        self.__load_absolute_indexed_register(0x01, "X"...)

        will result in us looking at memory address 0x01 + 0x04 = 0x05. If 0x05 contains 0x12 then 0x12 is loaded into
        the register using set_register_func.

        Args:
            address: The address to beign at
            register: The register to look at to get the offset to combine with address to get the final memory location
            set_register_func: A function accepting a value that sets the relevant register.
        """
        def get_offset():
            if register == "X":
                return self.x_register
            return self.y_register

        address_to_load = address + get_offset()
        set_register_func(self.__ram.get_address(address_to_load))

    def ldy_indexed_indirect(self, address):
        def set_register(val):
            self.y_register = val

        self.__load_indexed_indirect_register(address, set_register)

    def __load_indexed_indirect_register(self, address, set_register_func):
        """
        Indexed indirect addressing is done by taking the given address and adding the contents of the X register.

        This gives a new address. Load that and the next address along and combine them into a little-endian number to
        get another address. Load the contents of that address into the register.

        E.g. LDA $000C,X when x-register is 3 gives us a new address:

        0x000F

        0x000F contains 0x11. 0x0010 contains 0xFF. This give us a little-endian number that is the final address to visit:

        0xFF11, which contains 0x37.

        So 0x37 is the value to be loaded in to the accumulator.

        Args:
            address: The address that should have the X register added to it to begin the above process.
        """
        def get_hex_digits(hex_value):
            return str(hex_value).split('x')[1]

        first_address = address + self.x_register
        second_address = first_address + 0x01

        first_address_contents = self.__ram.get_address(first_address)
        second_address_contents = self.__ram.get_address(second_address)

        hex_string = "0x{first_digit}{second_digit}".format(first_digit=get_hex_digits(hex(second_address_contents)),
                                                            second_digit=get_hex_digits(hex(first_address_contents)))

        hex_number = int(hex_string, 0)
        set_register_func(self.__ram.get_address(hex_number))

class RegisterOverflowException(Exception):
    pass
