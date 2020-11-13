"""
File with utils functions to read CPT files. (file wih the information about how to set the colors of the models).
"""
from src.utils import get_logger

log = get_logger(module='CTP')

def read_file(filename: str):
    log.debug(f'Reading file {filename}')

    file = open(filename, 'r')

    colors = []
    for line in file.readlines():

        # dont consider comments
        if line[0] == '#':
            continue

        # dont consider final lines
        if line[0].isalpha():
            continue

        # only consider lines with code
        if len(line.split('\t')) < 4:
            continue

        # format values
        values = line.strip('\n').split('\t')
        while '' in values:
            values.remove('')

        # append
        if len(colors) == 0:
            colors.append({
                'height': float(values[0]),
                'color' : values[1].split('/')
            })
            colors.append({
                'height': float(values[2]),
                'color': values[3].split('/')
            })
        else:
            colors.pop()
            colors.append({
                'height': float(values[0]),
                'color' : values[1].split('/')
            })
            colors.append({
                'height': float(values[2]),
                'color': values[3].split('/')
            })

    return colors


if __name__ == '__main__':

    filename = 'test_colors/Ocean_Land_3.cpt'
    colors = read_file(filename)