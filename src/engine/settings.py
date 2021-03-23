"""
Python file with all the important constants and global variables of the engine.
"""


class Settings:
    # Screen settings
    WIDTH = 1300
    HEIGHT = 700
    MIN_WIDTH = 800
    MIN_HEIGHT = 600
    MAX_WIDTH = 99999
    MAX_HEIGHT = 99999

    # FRAME OPTIONS
    LEFT_FRAME_WIDTH = 300
    TOP_FRAME_HEIGHT = 0
    BOTTOM_FRAME_HEIGHT = 0
    MAIN_MENU_BAR_HEIGHT = 25

    # RENDER SETTINGS
    QUALITY = 25
    LINE_WIDTH = 1
    POLYGON_LINE_WIDTH = 2
    ACTIVE_POLYGON_LINE_WIDTH = POLYGON_LINE_WIDTH * 2
    DOT_SIZE = 1
    POLYGON_DOT_SIZE = 10

    # SCENE settings
    SCENE_BEGIN_X = LEFT_FRAME_WIDTH
    SCENE_BEGIN_Y = BOTTOM_FRAME_HEIGHT
    SCENE_WIDTH_X = WIDTH - LEFT_FRAME_WIDTH
    SCENE_HEIGHT_Y = HEIGHT - MAIN_MENU_BAR_HEIGHT

    VIEW_MODE = '2D'

    # GUI settings
    FONT_SIZE = 18
    TOOL_TITLE_FONT_SIZE = 25
    FIXED_FRAMES = True

    CLEAR_COLOR = [0.15, 0.15, 0.15, 1]  # clear color of the screen

    # type settings
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

        if Settings.FIXED_FRAMES:
            Settings.SCENE_BEGIN_X = Settings.LEFT_FRAME_WIDTH
            Settings.SCENE_BEGIN_Y = Settings.BOTTOM_FRAME_HEIGHT
            Settings.SCENE_WIDTH_X = Settings.WIDTH - Settings.LEFT_FRAME_WIDTH
            Settings.SCENE_HEIGHT_Y = Settings.HEIGHT - Settings.MAIN_MENU_BAR_HEIGHT - Settings.TOP_FRAME_HEIGHT
        else:
            Settings.SCENE_BEGIN_X = 0
            Settings.SCENE_BEGIN_Y = Settings.BOTTOM_FRAME_HEIGHT
            Settings.SCENE_WIDTH_X = Settings.WIDTH
            Settings.SCENE_HEIGHT_Y = Settings.HEIGHT - Settings.MAIN_MENU_BAR_HEIGHT - Settings.TOP_FRAME_HEIGHT
