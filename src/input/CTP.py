"""
File with utils functions to read CPT files. (file wih the information about how to set the colors of the models).
"""
from typing import List
from re import sub

from src.utils import get_logger

log = get_logger(module='CTP')


def is_numeric(text: str) -> bool:
    """
    Check if a string is numeric or not.

    Args:
        text: String to analyze.

    Returns:
        True if the string was numeric, False otherwise.

    """
    try:
        float(text)
        return True
    except ValueError:
        return False


def read_file(file_name: str) -> List[dict]:
    """
    Read a CTP file and extracts the colors and the limits associated to them.

    Return a list of dictionaries with the colors defined in CPT file in the same order as they are defined in the
    file.

    Important:
        This method does not delete repeated pairs of height/color that could be stored in the file.

    Example output:
        [{height: 0, color: [0,0,0]},
        {height: 100, color: [0,255,0]},
        {height: 100, color: [0,0,0]},
        {height: 200, color: [255,0,0]},
        ...]

    Args:
        file_name: Name of the file to read.

    Returns:
        Dictionary with the limits and the colors associated.

    """
    log.debug(f'Reading file {file_name}')

    file = open(file_name, 'r')

    color_pallet = []
    for line in file.readlines():

        # split the line to get the contents
        line = line.split()

        # do not consider empty lines
        if len(line) == 0:
            continue

        # dont consider lines not related to the definition of color
        if (not is_numeric(line[0])) or (not is_numeric(line[2])):
            continue

        # do not consider lines that does not have enough elements to define colors
        if len(line) < 4:
            continue

        # append
        values = line
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
    filename = '../../resources/test_resources/cpt/colors_0_100_200.cpt'
    colors = read_file(filename)
    print(colors)
