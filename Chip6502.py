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
            if val & 255 == 255:
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
        first_address = address + self.x_register
        hex_number = self.__combine_two_consecutive_address_values(first_address)
        set_register_func(self.__ram.get_address(hex_number))

    def __store_indexed_indirect_register(self, address, get_register_func):
        first_address = address + self.x_register
        hex_number = self.__combine_two_consecutive_address_values(first_address)
        self.__ram.set_address(hex_number, get_register_func())

    def __load_indirect_indexed_register(self, address, set_register_func):
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
        combined_address = self.__combine_two_consecutive_address_values(address)
        final_address = combined_address + self.y_register
        set_register_func(self.__ram.get_address(final_address))

    def __store_indirect_indexed_register(self, address, get_register_func):
        combined_address = self.__combine_two_consecutive_address_values(address)
        final_address = combined_address + self.y_register
        self.__ram.set_address(final_address, get_register_func())

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

class RegisterOverflowException(Exception):
    pass
