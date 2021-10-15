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
Python file with all the important constants and global variables of the engine.
"""


class Settings:
    """
    Static class that store the values of the settings in the application.

    Since the class is defined as static (all parameters are class parameters and not instance parameters), all changes
    to the parameters will affect every instance of the class, modifying the settings for the application.
    """

    # Screen settings
    WIDTH = 1300
    HEIGHT = 700
    MIN_WIDTH = 800
    MIN_HEIGHT = 600
    MAX_WIDTH = 99999
    MAX_HEIGHT = 99999

    # Extra reload proportion to use when reloading indices
    EXTRA_RELOAD_PROPORTION = 1.3

    # FRAME OPTIONS
    LEFT_FRAME_WIDTH = 315
    TOP_FRAME_HEIGHT = 0
    BOTTOM_FRAME_HEIGHT = 0
    MAIN_MENU_BAR_HEIGHT = 25

    # CAMERA SETTINGS
    FIELD_OF_VIEW = 30
    PROJECTION_NEAR = 0.1
    PROJECTION_FAR = 3000

    # RENDER SETTINGS
    QUALITY = 1
    LINE_WIDTH = 1
    POLYGON_LINE_WIDTH = 2
    ACTIVE_POLYGON_LINE_WIDTH = POLYGON_LINE_WIDTH * 2
    DOT_SIZE = 1
    POLYGON_DOT_SIZE = 10

    # SCENE settings
    SCENE_BEGIN_X = LEFT_FRAME_WIDTH
    SCENE_BEGIN_Y = BOTTOM_FRAME_HEIGHT
    SCENE_WIDTH_X = WIDTH - LEFT_FRAME_WIDTH
    SCENE_HEIGHT_Y = HEIGHT - MAIN_MENU_BAR_HEIGHT - TOP_FRAME_HEIGHT
    CLEAR_COLOR = [0.15, 0.15, 0.15, 1]  # clear color of the screen

    # GUI settings
    FIXED_FRAMES = True

    # Type settings
    FLOAT_BYTES = 4  # float will be represented by 4 bytes.

    @staticmethod
    def fix_frames(fix_frames: bool) -> None:
        """
        Select if the frames are fixed or not in the program.

        Args:
            fix_frames: if the frames are fixed in the application or not.

        Returns: None
        """
        Settings.FIXED_FRAMES = fix_frames
        Settings.update_scene_values()

    @staticmethod
    def update_scene_values() -> None:
        """
        Update the settings related to the scene.

        Returns: None
        """

        # Update the scene values depending if the frames are fixed on the application or if they are movable.
        # ----------------------------------------------------------------------------------------------------
        if Settings.FIXED_FRAMES:
            Settings.SCENE_BEGIN_X = Settings.LEFT_FRAME_WIDTH
            Settings.SCENE_BEGIN_Y = Settings.BOTTOM_FRAME_HEIGHT
            Settings.SCENE_WIDTH_X = Settings.WIDTH - Settings.LEFT_FRAME_WIDTH
            Settings.SCENE_HEIGHT_Y = Settings.HEIGHT - Settings.MAIN_MENU_BAR_HEIGHT - Settings.TOP_FRAME_HEIGHT
        else:
            Settings.SCENE_BEGIN_X = 0
            Settings.SCENE_BEGIN_Y = 0
            Settings.SCENE_WIDTH_X = Settings.WIDTH
            Settings.SCENE_HEIGHT_Y = Settings.HEIGHT - Settings.MAIN_MENU_BAR_HEIGHT
