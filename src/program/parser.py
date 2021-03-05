"""
File that contains functionality to get and configure a parser for the command line options.
"""
import argparse


def get_command_line_arguments() -> 'argparse.Namespace':
    """
    Configure and return a command line parser.

    Returns: Parser to use to get the arguments.
    """
    parser = argparse.ArgumentParser(description='Relief creator Program.')
    parser.add_argument('-model', metavar='<filename>', type=str,
                        help='A netcdf to load before running the program.')

    args = parser.parse_args()
    return args
