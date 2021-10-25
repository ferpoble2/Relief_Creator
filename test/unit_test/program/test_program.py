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
File with tests related to the Program class of the application.
"""
import os
import sys
import unittest

from src.program.parser import get_command_line_arguments
from src.program.program import Program
from src.program.tools import Tools
from src.program.view_mode import ViewMode
from test.test_case import ProgramTestCase


class TestZoomParameters(ProgramTestCase):

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


class TestViewModeParameters(ProgramTestCase):

    def test_view_mode(self):
        # Default value
        self.assertEqual(ViewMode.mode_2d, self.program.get_view_mode())

        # Change values
        self.program.set_view_mode_3D()
        self.assertEqual(ViewMode.mode_3d, self.program.get_view_mode())

        self.program.set_view_mode_2D()
        self.assertEqual(ViewMode.mode_2d, self.program.get_view_mode())


class TestMapPositionParameters(ProgramTestCase):

    def test_map_position(self):
        # Default value
        self.assertEqual([0, 0], self.program.get_map_position())

        # Move map
        self.program.set_map_position([15, 15])
        self.assertEqual([15, 15], self.program.get_map_position())


class TestActiveToolParameters(ProgramTestCase):

    def test_active_tool(self):
        # Default value
        self.assertEqual(None, self.program.get_active_tool())

        # Test all the tools in the program
        self.program.set_active_tool(Tools.move_map)
        self.assertEqual(Tools.move_map, self.program.get_active_tool())

        self.program.set_active_tool(Tools.create_polygon)
        self.assertEqual(Tools.create_polygon, self.program.get_active_tool())

        # Test exception raised
        with self.assertRaises(KeyError):
            self.program.set_active_tool('non_existent_tool')


class TestLoadingParameters(ProgramTestCase):

    def test_is_loading(self):
        self.assertEqual(False, self.program.is_loading())

        self.program.set_loading(True)
        self.assertEqual(True, self.program.is_loading())

        self.program.set_loading(False)
        self.assertEqual(False, self.program.is_loading())


class TestCPTFilesParameters(ProgramTestCase):

    def test_cpt_files(self):
        # Default value
        default_value = os.path.join(os.getcwd(), 'resources', 'colors', 'default.cpt')
        self.assertEqual(default_value, self.program.get_cpt_file())

        # Change the file
        self.program.set_cpt_file('resources/test_resources/cpt/colors_0_100_200.cpt')
        self.assertEqual('resources/test_resources/cpt/colors_0_100_200.cpt', self.program.get_cpt_file())


class TestDebugMode(unittest.TestCase):

    def test_debug_mode_default_value(self):
        program = Program()

        self.assertFalse(program.get_debug_mode())

        program.close()

    def test_debug_mode_false(self):
        program = Program(debug_mode=True)

        self.assertTrue(program.get_debug_mode())

        program.close()


class TestParser(ProgramTestCase):

    def test_parser_model(self):

        saved_argv = sys.argv

        try:
            sys.argv = ['./main.py', '-model', 'resources/sample_netcdf/ETOPO_IceSurfacec_6m.nc']
            arguments = get_command_line_arguments()

            self.assertIsNone(self.program.get_active_model())

            self.program.process_arguments(arguments)
            self.assertIsNotNone(self.program.get_active_model())

        finally:
            sys.argv = saved_argv


class TestSetCPT(unittest.TestCase):

    def test_not_cpt_file(self):
        program = Program()

        with self.assertRaises(IOError):
            program.set_cpt_file('Non_Existent_File.something')

    def test_default_value(self):
        program = Program()
        self.assertEqual(os.path.join(os.getcwd(), 'resources', 'colors', 'default.cpt'),
                         program.get_cpt_file(),
                         'Default CPT value is not equal to the expected.')

    def test_normal_assignation(self):
        program = Program()
        program.set_cpt_file('colors.cpt')  # This file does not exists.
        self.assertEqual('colors.cpt', program.get_cpt_file())


if __name__ == '__main__':
    unittest.main()
