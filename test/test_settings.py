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
from src.engine.settings import Settings


class TestFixFrames(unittest.TestCase):

    def test_fix_frames_method(self):
        # Default value
        self.assertTrue(Settings.FIXED_FRAMES)

        # Change value
        Settings.fix_frames(False)
        self.assertFalse(Settings.FIXED_FRAMES)

        Settings.fix_frames(True)
        self.assertTrue(Settings.FIXED_FRAMES)

    def test_update_scene_values(self):
        # Default values
        self.assertEqual(Settings.LEFT_FRAME_WIDTH, Settings.SCENE_BEGIN_X)
        self.assertEqual(Settings.BOTTOM_FRAME_HEIGHT, Settings.SCENE_BEGIN_Y)
        self.assertEqual(Settings.WIDTH - Settings.LEFT_FRAME_WIDTH, Settings.SCENE_WIDTH_X)
        self.assertEqual(Settings.HEIGHT - Settings.MAIN_MENU_BAR_HEIGHT - Settings.TOP_FRAME_HEIGHT,
                         Settings.SCENE_HEIGHT_Y)

        # Change Values
        Settings.fix_frames(False)
        self.assertEqual(0, Settings.SCENE_BEGIN_X)
        self.assertEqual(0, Settings.SCENE_BEGIN_Y)
        self.assertEqual(Settings.WIDTH, Settings.SCENE_WIDTH_X)
        self.assertEqual(Settings.HEIGHT - Settings.MAIN_MENU_BAR_HEIGHT,
                         Settings.SCENE_HEIGHT_Y)

        Settings.fix_frames(True)
        self.assertEqual(Settings.LEFT_FRAME_WIDTH, Settings.SCENE_BEGIN_X)
        self.assertEqual(Settings.BOTTOM_FRAME_HEIGHT, Settings.SCENE_BEGIN_Y)
        self.assertEqual(Settings.WIDTH - Settings.LEFT_FRAME_WIDTH, Settings.SCENE_WIDTH_X)
        self.assertEqual(Settings.HEIGHT - Settings.MAIN_MENU_BAR_HEIGHT - Settings.TOP_FRAME_HEIGHT,
                         Settings.SCENE_HEIGHT_Y)


if __name__ == '__main__':
    unittest.main()
