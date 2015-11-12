class NesMemory(object):

    def __init__(self, memory_size):
        self.memory_size = memory_size
        self.ram = []
        self.__init_memory()

    def __init_memory(self):
        for i in range(self.memory_size):
            self.ram.append(0x00)

    def set_address(self, address, value):
        """
        Set an address in memory to the given value.

        Address locations can store an eight-bit value, so valid values are from 0x00 to 0xFF.

        Addresses 0x00 to 0x7FF inclusive are mirrored in addresses 0x801 to 0x2000. Setting an address in one range
        results in the corresponding address in the other range being set to the same value.

        Args:
            address: The memory address to set. Valid values are from 0x00 to self.__memory_size
            value: The eight-bit value to set the address to.

        Raises:
            MemorySlotOverflowException if the length of value is > 0xFF.
        """

        address_should_be_mirrored_upward = lambda: 0x00 <= address <= 0x7FF
        address_should_be_mirrored_downward = lambda: 0x801 <= address <= 0x2000

        if value > 0xFF:
            raise MemorySlotOverflowException

        self.ram[address] = value

        if address_should_be_mirrored_upward(): self.ram[address + 0x801] = value
        if address_should_be_mirrored_downward(): self.ram[address - 0x801] = value

    def get_address(self, address):
        return self.ram[address]

    def get_absolute_indexed_address(self, base_address, get_offset_func):
        """
        Get the memory address that is the base address plus the value retrieved by executing an offset function.

        The offset function is intended to retrieve the value of the chip's X or Y register.

        e.g. If address given is 0x01 and the X-register contains 0x04, then the following call:

        get_absolute_indexed_address(0x01, get_x_register)

        Where get_x_register returns a valu of 0x02 will result 0x01 + 0x02 = 0x03 being returned.

        Args:
            base_address: The memory address to begin from
            get_offset_func: A function that returns the offset to add to base_address

        Returns:
            The absolute indexed memory address in relation to base_address and the result of get_offset_func
        """
        return base_address + get_offset_func()

    def get_indexed_indirect_memory_address(self, address, x_register):
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
        first_address = address + x_register
        return self.__combine_two_consecutive_address_values(first_address)

    def get_indirect_indexed_memory_address(self, address, y_register):
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
        return combined_address + y_register

    def __combine_two_consecutive_address_values(self, first_address):

        def get_two_consecutive_address_values(first_address):
            return (self.get_address(first_address), self.get_address(first_address+0x01))

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

class MemorySlotOverflowException(Exception):
    pass
