"""
File with the class InterpolationTools. Class in charge of render the Interpolation Tools inside another frame.
"""

import imgui

from src.utils import get_logger

log = get_logger(module="INTERPOLATION_TOOLS")


class InterpolationTools:
    """
    Class that render the interpolation tools inside another frame.
    """

    # noinspection PyUnresolvedReferences
    def __init__(self, gui_manager: 'GUIManager'):
        """
        Constructor of the class.
        """
        self.__gui_manager = gui_manager

        self.__combo_options = ['Linear']
        self.__current_combo_option = 0

        self.__distance_current_value = 0

    def render(self) -> None:
        """
        Render the interpolation tools to modify the borders of the polygons modifications.
        Returns: None
        """
        self.__gui_manager.set_tool_title_font()
        imgui.text('Interpolation Tools')
        self.__gui_manager.set_regular_font()

        clicked, self.__current_combo_option = imgui.combo(
            "Type", self.__current_combo_option, self.__combo_options
        )

        _, self.__distance_current_value = imgui.input_float('Distance', self.__distance_current_value)

        if imgui.button('Interpolate', -1):
            log.debug('Interpolating points.')

