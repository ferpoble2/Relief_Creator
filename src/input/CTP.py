"""
File with utils functions to read CPT files. (file wih the information about how to set the colors of the models).
"""
from typing import List

from src.utils import get_logger

log = get_logger(module='CTP')


def read_file(file_name: str) -> List[dict]:
    """
    Read a CTP file and extracts the colors and the limits associated to them

    Args:
        file_name: Name of the file to read.

    Returns: Dictionary with the limits and the colors associated.

    """
    log.debug(f'Reading file {file_name}')

    file = open(file_name, 'r')

    color_pallet = []
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
        if len(color_pallet) == 0:
            color_pallet.append({
                'height': float(values[0]),
                'color': values[1].split('/')
            })
            color_pallet.append({
                'height': float(values[2]),
                'color': values[3].split('/')
            })
        else:
            color_pallet.pop()
            color_pallet.append({
                'height': float(values[0]),
                'color': values[1].split('/')
            })
            color_pallet.append({
                'height': float(values[2]),
                'color': values[3].split('/')
            })

    return color_pallet


if __name__ == '__main__':
    filename = 'test_colors/Ocean_Land_3.cpt'
    colors = read_file(filename)
