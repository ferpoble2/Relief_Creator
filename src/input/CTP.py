"""
File with utils functions to read CPT files. (file wih the information about how to set the colors of the models).
"""
import logging as log


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
            print('f')
            colors.append({
                'height': int(values[0]),
                'color' : values[1].split('/')
            })
            colors.append({
                'height': int(values[2]),
                'color': values[3].split('/')
            })
        else:
            print('s')
            colors.pop()
            colors.append({
                'height': int(values[0]),
                'color' : values[1].split('/')
            })
            colors.append({
                'height': int(values[2]),
                'color': values[3].split('/')
            })

    return colors


if __name__ == '__main__':
    log.basicConfig(format="%(asctime)s - %(message)s", level=log.DEBUG)

    filename = 'test_colors/Ocean_Land_3.cpt'
    colors = read_file(filename)
    print(colors)