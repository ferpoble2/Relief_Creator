#  BEGIN GPL LICENSE BLOCK
#
#      This program is free software: you can redistribute it and/or modify
#      it under the terms of the GNU General Public License as published by
#      the Free Software Foundation, either version 3 of the License, or
#      (at your option) any later version.
#
#      This program is distributed in the hope that it will be useful,
#      but WITHOUT ANY WARRANTY; without even the implied warranty of
#      MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#      GNU General Public License for more details.
#
#      You should have received a copy of the GNU General Public License
#      along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
#  END GPL LICENSE BLOCK

"""
Tests related to the logic of the parser of arguments of the program.

The parser is the module in charge of executing logic depending of the parameters given when executing
the program from the console
"""

import unittest
import sys

from src.program.parser import get_command_line_arguments


class TestArgumentParser(unittest.TestCase):

    def test_argument_reading(self):

        arguments = get_command_line_arguments()
        self.assertIn('model', arguments)
        self.assertIsNone(arguments.model)

    def test_argument_model_value(self):

        saved_argv = sys.argv

        try:
            sys.argv = ['./main.py', '-model', 'resources/sample_netcdf/ETOPO_IceSurfacec_6m.nc']

            arguments = get_command_line_arguments()

            self.assertIn('model', arguments)
            self.assertEqual('resources/sample_netcdf/ETOPO_IceSurfacec_6m.nc',
                             arguments.model)
        finally:
            sys.argv = saved_argv


if __name__ == '__main__':
    unittest.main()
