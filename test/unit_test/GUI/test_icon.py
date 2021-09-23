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

import unittest

from src.engine.GUI.icon import Icon
from test.test_case import ProgramTestCase


class TestIconCreation(ProgramTestCase):

    def test_RGB_file(self):
        # Test the creation and id of the icon
        # ------------------------------------
        icon = Icon('resources/test_resources/images/rgb.png')
        self.assertEqual(3, icon.get_texture_id())

    def test_RGBA_file(self):
        # Test the creation and id of the icon
        # ------------------------------------
        icon = Icon('resources/test_resources/images/rgba.png')
        self.assertEqual(3, icon.get_texture_id())

    def test_not_implemented_image_mode(self):
        # Test the creation and id of the icon
        # ------------------------------------
        with self.assertRaises(NotImplementedError):
            icon = Icon('resources/test_resources/images/grayscale.png')


if __name__ == '__main__':
    unittest.main()
