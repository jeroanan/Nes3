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

def clear_negative_flag_func(chip):
    def clear_negative_flag():
        chip.negative_flag = 0x0
    return clear_negative_flag

def get_negative_flag_func(chip):
    def get_negative_flag():
        return chip.negative_flag
    return get_negative_flag

def clear_overflow_flag_func(chip):
    def clear_overflow_flag():
        chip.overflow_flag = 0x0
    return clear_overflow_flag

def get_overflow_flag_func(chip):
    def get_overflow_flag():
        return chip.overflow_flag
    return get_overflow_flag

def get_clear_zero_flag_func(chip):
    def clear_zero_flag():
        chip.zero_flag = 0x0
    return clear_zero_flag

def get_zero_flag_func(chip):
    def get_zero_flag():
        return chip.zero_flag
    return get_zero_flag
