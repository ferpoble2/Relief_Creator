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
import logging
import json

# Get the keys to search in the reading process of the NetCDF file from the files located in the resources.
# ---------------------------------------------------------------------------------------------------------
with open('resources/longitude_keys.json', 'r') as lon_file:
    LONGITUDE_KEYS = json.load(lon_file)
with open('resources/latitude_keys.json', 'r') as lat_file:
    LATITUDE_KEYS = json.load(lat_file)
with open('resources/height_keys.json', 'r') as height_file:
    HEIGHT_KEYS = json.load(height_file)

# Configurations of the loggers. These configurations affect all the loggers of the application.
# ----------------------------------------------------------------------------------------------
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


def interpolate(value: float, value_min: float, value_max: float, target_min: float = -1,
                target_max: float = 1, convert: bool = True) -> float:
    """
    Interpolate the given value between the other specified values.

    To interpolate the value between the target values it is necessary to specify an initial interval in which
    the value exists (value_min and value_max) and the target interval to interpolate it (target_min and target_max).

    If value_min and value_max are equal, then average between the targets values will be returned.

    Args:
        convert: True to convert the value to float
        value: Value to interpolate.
        value_min: Minimum value of the values.
        value_max: Maximum value of the values.
        target_min: Minimum value of the interpolation interval.
        target_max: Maximum value of the interpolation interval.

    Returns: Interpolated value.
    """
    if convert:
        value = float(value)

    # check values
    value_min, value_max = min(value_min, value_max), max(value_min, value_max)
    target_min, target_max = min(target_min, target_max), max(target_min, target_max)

    # case initial interval is just one value.
    if value_min == value_max:
        return (target_min + target_max) / 2.0

    if target_min == target_max:
        return target_max

    # return corresponding values
    return (value - value_min) * (float(target_max) - target_min) / (float(value_max) - value_min) + target_min


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

    # points is your list (or array) of 2d points.
    assert len(points) > 2, 'Need at least 3 points to work.'

    s = 0.0
    for p1, p2 in zip(points, points[1:] + [points[0]]):
        s += (p2[0] - p1[0]) * (p2[1] + p1[1])
    return s > 0.0
