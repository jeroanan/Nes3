import unittest

import NesMemory as memory


class TestNesMemory(unittest.TestCase):

    def setUp(self):
        self.__max_address = 0xFFFF
        self.__target = memory.NesMemory(self.__max_address)

    def test_ram_allocated_to_right_size(self):
        self.assertEqual(self.__max_address, len(self.__target.ram))

    def test_ram_is_zeroed(self):
        """
        When the memory is powered up it is expected for it all to be set to zero
        """
        non_zeroed_ram = [x for x in self.__target.ram if x != 0x00]
        self.assertEqual(0, len(non_zeroed_ram))

    def test_set_address_too_high_raises_memory_slot_overflow_exception(self):
        """
        Each memory address is eight bits long. So setting it to something longer than eight bits can hold will result
        in a MemorySlotOverflowException being raised.
        """
        self.assertRaises(memory.MemorySlotOverflowException, self.__target.set_address, 0x01, 0x100)
        self.assertEqual(0x00, self.__target.ram[0x01])

    def test_set_lower_mirrored_address_sets_counterpart_higher_mirrored_address(self):
        """
        If memory addresses 0x00 to 0x7FF are set, the value being set should be mirrored in the range 0x801 to 0x2000.

        This leaves memory address 0x800 unmirrored. I haven't seen any docs saying 0x800 should be mirrored, but it's
        something to bear in mind.
        """
        self.__assert_address_is_mirrored(0x01, 0x801)

    def test_set_higher_mirrored_address_sets_counterpart_lower_mirrored_address(self):
        """
        If a memory address of 0x801 <= address <= 0x2000 is set then the address - 0x801 should also be set
        to the same value
        """
        self.__assert_address_is_mirrored(0x802, -0x801)

    def test_set_address_above_lower_mirrored_range_does_not_set_higher_address(self):
        """
        If a memory address > 0x7FF is set, we do not want a memory address of address + 0x801 to be set.
        """
        self.__assert_set_address_is_not_mirrored(0x800, 0x801)

    def test_set_address_above_higher_mirrored_range_does_not_set_lower_address(self):
        """
        If a memory addess > 0x2000 is set, we do not want a memory address of address - 0x801 to be set.
        """
        self.__assert_set_address_is_not_mirrored(0x2001, -0x801)

    def __assert_address_is_mirrored(self, address, offset):
        self.__assert_address_mirroring(address, offset, 0x0E, 0x0E)

    def __assert_set_address_is_not_mirrored(self, address, offset):
        self.__assert_address_mirroring(address, offset, 0x0E, 0x00)

    def __assert_address_mirroring(self, address, offset, memory_value, mirrored_value):
        offset_address = address + offset
        self.__target.set_address(address, memory_value)
        offset_address_value = self.__target.get_address(offset_address)
        self.assertEqual(mirrored_value, offset_address_value)

    def test_get_absolute_indexed_address(self):
        def get_offset():
            return 0x01

        base_address = 0x02
        self.assertEqual(0x03, self.__target.get_absolute_indexed_address(base_address, get_offset))

    
