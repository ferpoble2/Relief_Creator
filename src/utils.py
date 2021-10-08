# BEGIN GPL LICENSE BLOCK
#
#     This program is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# END GPL LICENSE BLOCK

"""
File with utils functions for the engine.
"""
import json
import logging
from typing import Union

import numpy as np

# Get the keys to search in the reading process of the NetCDF file from the files located in the resources.
with open('resources/longitude_keys.json', 'r') as lon_file:
    LONGITUDE_KEYS = json.load(lon_file)
with open('resources/latitude_keys.json', 'r') as lat_file:
    LATITUDE_KEYS = json.load(lat_file)
with open('resources/height_keys.json', 'r') as height_file:
    HEIGHT_KEYS = json.load(height_file)

# Configurations of the loggers. These configurations affect all the loggers of the application.
LOG_TO_FILE = False
LOG_TO_CONSOLE = False

LOG_LEVEL = logging.DEBUG
LOG_FILE_LEVEL = logging.DEBUG

LOG_ONLY_LISTED_MODULES = False
LOG_LIST_MODULES = [
    'CONTROLLER',
    'ENGINE',
    'PROGRAM',
    'SCENE',
    'TEXT_MODAL',
    'MAP3DMODEL'
]


def get_logger(log_level: int = LOG_LEVEL,
               log_file_level: int = LOG_FILE_LEVEL,
               module: str = 'GLOBAL',
               directory: str = f'resources/logs',
               log_to_file: bool = LOG_TO_FILE,
               log_to_console: bool = LOG_TO_CONSOLE,
               log_only_listed_modules: bool = LOG_ONLY_LISTED_MODULES,
               log_list_modules: list = LOG_LIST_MODULES) -> logging.Logger:
    """
    Get the logger of the application to use in the main program.

    To make use of the logger, use the function as follows:
        log = get_logger(module='SOME_MODULE')
        ...
        log.debug('some debug info')

    Most of the configuration for the logger is set on the module that defines this function. Only change the
    default values for the method in case you are testing the function or doing another thing outside the main
    program.

    Args:
        log_list_modules: List of modules to log if log_only_listed_modules is true.
        log_only_listed_modules: If to log only the modules listed on the log_list_modules parameter or not.
        log_to_console: If to log to console or not.
        log_to_file: If to log to file or not.
        directory: Directory to use to create the log file if logging to file.
        module: Module being logged. (mus be written in uppercase)
        log_file_level: Level to show in the file logs (logging.DEBUG, logging.INFO, ...)
        log_level: Level to show in the logs (logging.DEBUG, logging.INFO, ...)

    Returns: Logger to use to makes logs.

    """
    log = logging.getLogger(module)
    log.propagate = False
    log.setLevel(log_level)

    formatter = logging.Formatter(f"%(asctime)s.%(msecs)03d - {module} - %(levelname)s: %(message)s",
                                  datefmt='%Y-%m-%d,%H:%M:%S')

    handlers = []
    if log_to_file:
        fh = logging.FileHandler(f'{directory}/{module}.log')
        fh.setLevel(log_file_level)
        fh.setFormatter(formatter)
        handlers.append(fh)

    if log_to_console:
        ch = logging.StreamHandler()
        ch.setLevel(log_level)
        ch.setFormatter(formatter)
        handlers.append(ch)

    if log_only_listed_modules:
        if module in log_list_modules:
            log.handlers = handlers
    else:
        log.handlers = handlers

    return log


def is_numeric(value: str) -> bool:
    """
    Check if a value can be converted to float.

    Args:
        value: value to check

    Returns: boolean indicating if can be converted
    """
    try:
        float(value)
        return True
    except ValueError:
        return False


def is_clockwise(points):
    """
    Check if a list of 2D points are in CW order or not.

    Args:
        points: List of 2D points [(1.x,1.y),(2.x,2.y),...]

    Returns: Boolean indicating if points are CW or not.
    """
    assert len(points) > 2, 'Need at least 3 points to work.'

    s = 0.0
    for p1, p2 in zip(points, points[1:] + [points[0]]):
        s += (p2[0] - p1[0]) * (p2[1] + p1[1])
    return s > 0.0


def list_to_serializable_list(list_obj: Union[list, tuple]) -> list:
    """
    Converts all the values in a list to arguments serializable on a json file.

    Args:
        list_obj: List to serialize

    Returns: New List with the new serializable values.
    """
    serializable_list = []
    for value in list_obj:
        if type(value) == np.ndarray:
            serializable_list.append(value.tolist())
        elif type(value) == dict:
            serializable_list.append(dict_to_serializable_dict(value))
        else:
            serializable_list.append(value)
    return serializable_list


def dict_to_serializable_dict(dictionary) -> dict:
    """
    Converts all the values in a dictionary to arguments serializable on a json file.

    Args:
        dictionary: Dictionary to serialize

    Returns: New dictionary with the new arguments.
    """
    dict_cpy = dict(dictionary)
    for key, value in dict_cpy.items():
        if type(value) == np.ndarray:
            dict_cpy[key] = value.tolist()
        elif type(value) == dict:
            dict_cpy[key] = dict_to_serializable_dict(value)
        elif type(value) == tuple or type(value) == list:
            dict_cpy[key] = list_to_serializable_list(value)

    return dict_cpy


def json_to_dict(json_filename: str) -> dict:
    """
    Read the data inside a JSON file.

    Args:
        json_filename: File to read the information.

    Returns: Dictionary with the values stored on the JSON file.
    """
    with open(json_filename) as json_file:
        data = json.load(json_file)

    return data


def dict_to_json(dictionary: dict, json_filename: str) -> None:
    """
    Store the values in the dictionary on a JSON file.

    If values are numpy arrays, then this method convert those values to list before storing them in the JSON file.

    Args:
        dictionary: Dictionary to store in a JSON file.
        json_filename: Filename of the generated file.

    Returns: None
    """
    new_dict = dict_to_serializable_dict(dictionary)
    with open(json_filename, 'w') as fp:
        json.dump(new_dict, fp)
