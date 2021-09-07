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
Module with test related to the engine of the program.
"""

import unittest

from src.engine.engine import Engine
from src.program.program import Program


class TestViewMode(unittest.TestCase):

    def test_default_view_mode(self):
        engine = Engine()
        program = Program(engine, initialize_engine=False)

        self.assertEqual('2D',
                         program.get_view_mode(),
                         '2D is not the default mode when creating the program.')

    def test_view_mode_3D(self):
        engine = Engine()
        program = Program(engine, initialize_engine=False)

        engine.set_program_view_mode('3D')
        self.assertEqual('3D',
                         program.get_view_mode(),
                         'Mode was not changed to 3D after calling set_program_view_mode')

    def test_view_mode_2D(self):
        engine = Engine()
        program = Program(engine, initialize_engine=False)

        engine.set_program_view_mode('3D')
        engine.set_program_view_mode('2D')
        self.assertEqual('2D',
                         program.get_view_mode(),
                         'Mode was not changed to 2D after calling set_program_view_mode')


if __name__ == '__main__':
    unittest.main()
