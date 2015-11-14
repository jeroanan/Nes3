def get_accumulator_func(chip):
    def get_accumulator():
        return chip.accumulator
    return get_accumulator

def set_accumulator_func(chip):
    def set_accumulator(value):
        chip.accumulator = value
    return set_accumulator

def get_x_register_func(chip):
    def get_x_register():
        return chip.x_register
    return get_x_register

def set_x_register_func(chip):
    def set_x_register(value):
        chip.x_register = value
    return set_x_register

def get_y_register_func(chip):
    def get_y_register():
        return chip.y_register
    return get_y_register

def set_y_register_func(chip):
    def set_y_register(value):
        chip.y_register = value
    return set_y_register
