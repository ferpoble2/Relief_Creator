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
File that contains functionality to get and configure a parser for the command line options.

The parser will do logic on the program accordingly to the options given in the command.
"""
import argparse


def get_command_line_arguments() -> 'argparse.Namespace':
    """
    Configure and return a command line parser.

    The command line parser returned works as a dictionary that can be asked if the parameters expected were defined
    when the call to run the program was made.

    Example:
        if 'model' in parser:
            ...

        if parser.model is not None:
            ...

    Returns: Parser to use to get the arguments.
    """
    parser = argparse.ArgumentParser(description='Relief creator Program.')
    parser.add_argument('-model', metavar='<filename>', type=str,
                        help='A netcdf to load before running the program.')
    parser.add_argument('-debug', action='store_true',
                        help='If to start the program in debug mode.')

    args = parser.parse_args()
    return args
