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

import os
import unittest

from src.engine.engine import Engine
from src.program.program import Program


class TestProgramParameters(unittest.TestCase):

    def setUp(self) -> None:
        """
        Code executed before every test. Initializes a program to work with.
        """
        # create program
        self.engine = Engine()
        self.program = Program(self.engine)

        # initialize variables
        self.engine.should_use_threads(False)

    def tearDown(self) -> None:
        """
        Delete all temporary files created by the program on the setup or testing processes.

        Returns: None
        """
        self.program.close()

    def test_zoom(self):
        # Test default values
        self.assertEqual(1, self.program.get_zoom_level())

        # Test when adding zoom
        self.program.add_zoom()
        self.assertEqual(2, self.program.get_zoom_level())

        self.program.add_zoom()
        self.program.add_zoom()
        self.assertEqual(4, self.program.get_zoom_level())

        # Test when subtracting zoom
        self.program.less_zoom()
        self.program.less_zoom()
        self.program.less_zoom()
        self.assertEqual(1, self.program.get_zoom_level())

        self.program.less_zoom()
        self.assertEqual(0.5, self.program.get_zoom_level())

        self.program.less_zoom()
        self.assertEqual(0.25, self.program.get_zoom_level())

        # Return to the original values
        self.program.add_zoom()
        self.program.add_zoom()
        self.assertEqual(1, self.program.get_zoom_level())

    def test_view_mode(self):
        # Default value
        self.assertEqual('2D', self.program.get_view_mode())

        # Change values
        self.program.set_view_mode_3D()
        self.assertEqual('3D', self.program.get_view_mode())

        self.program.set_view_mode_2D()
        self.assertEqual('2D', self.program.get_view_mode())

    def test_map_position(self):
        # Default value
        self.assertEqual([0, 0], self.program.get_map_position())

        # Move map
        self.program.set_map_position([15, 15])
        self.assertEqual([15, 15], self.program.get_map_position())

    def test_active_tool(self):
        # Default value
        self.assertEqual(None, self.program.get_active_tool())

        # Test all the tools in the program
        self.program.set_active_tool('move_map')
        self.assertEqual('move_map', self.program.get_active_tool())

        self.program.set_active_tool('create_polygon')
        self.assertEqual('create_polygon', self.program.get_active_tool())

        # Test exception raised
        with self.assertRaises(KeyError):
            self.program.set_active_tool('non_existent_tool')

    def test_is_loading(self):
        self.assertEqual(False, self.program.is_loading())

        self.program.set_loading(True)
        self.assertEqual(True, self.program.is_loading())

        self.program.set_loading(False)
        self.assertEqual(False, self.program.is_loading())

    def test_cpt_files(self):
        # Default value
        default_value = os.path.join(os.getcwd(), 'resources', 'colors', 'default.cpt')
        self.assertEqual(default_value, self.program.get_cpt_file())

        # Change the file
        self.program.set_cpt_file('resources/test_resources/cpt/colors_0_100_200.cpt')
        self.assertEqual('resources/test_resources/cpt/colors_0_100_200.cpt', self.program.get_cpt_file())


if __name__ == '__main__':
    unittest.main()
