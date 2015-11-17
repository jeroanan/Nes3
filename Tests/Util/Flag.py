def get_carry_flag_func(chip):
    def get_carry_flag():
        return chip.carry_flag
    return get_carry_flag

def set_carry_flag_func(chip):
    def set_carry_flag():
        chip.carry_flag = 0x1
    return set_carry_flag

def clear_carry_flag_func(chip):
    def clear_carry_flag():
        chip.carry_flag = 0x0
    return clear_carry_flag

def set_overflow_flag_func(chip):
    def set_overflow_flag():
        chip.overflow_flag = 0x1
    return set_overflow_flag

def clear_overflow_flag_func(chip):
    def clear_overflow_flag():
        chip.overflow_flag = 0x0
    return clear_overflow_flag

def get_overflow_flag_func(chip):
    def get_overflow_flag():
        return chip.overflow_flag
    return get_overflow_flag
