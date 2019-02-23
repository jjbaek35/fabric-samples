

def compare_buffers(buffer_a, buffer_b):
    match = 1
    if len(buffer_a) != len(buffer_b):
        print('Buffer Lengths do not match')
        return False
    for i in range(len(buffer_a)):
        if buffer_a[i] != buffer_b[i]:
            print(i)
            match = 0
            return False
    if match == 1:
        return True


def convert_unsigned_byte_array_to_string(ubyte_array):
    string = ''
    for i in ubyte_array:
        string += str(i) + '_'
    return string[:-1]  # Takes care of the last _


def compare_string_to_unsigned_byte_array(string, ubyte_array):
    buffer_a = [int(i) for i in string]
    return compare_buffers(buffer_a, buffer_b=ubyte_array)


def split_incoming_command(device_type, data, delimeter=':'):
    if device_type == 'inverter':
        pass
    if device_type == 'utility':
        pass
