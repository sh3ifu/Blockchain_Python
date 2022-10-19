import json


def read_from_file(filepath, mode='r', js=True, readlines=False):
    file = open(filepath, mode)
    
    if js:
        data = json.load(file)
    elif readlines:
        data = file.read().splitlines()
    else:
        data = file.read()
    
    file.close()

    return data


def write_to_file(data, filepath, mode='a'):
    file = open(filepath, mode)
    file.write(data)
    file.close()


def delete_in_file(filepath, lines_count):
    data = read_from_file(filepath, js=False, readlines=True)
    data = data[lines_count:]
    data = str('\n'.join(data))
    write_to_file(data, filepath, mode='w')
