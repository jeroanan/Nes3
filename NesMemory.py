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


class MemorySlotOverflowException(Exception):
    pass
