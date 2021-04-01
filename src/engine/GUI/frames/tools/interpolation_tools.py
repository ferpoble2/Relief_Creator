"""
File with the class InterpolationTools. Class in charge of render the Interpolation Tools inside another frame.
"""

import imgui

from src.utils import get_logger
from src.error.interpolation_error import InterpolationError

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

        self.__combo_options = ['linear', 'nearest', 'cubic']
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
        if self.__distance_current_value < 0:
            self.__distance_current_value = 0

        if imgui.button('Interpolate', -1):
            log.debug('Interpolating points.')
            try:
                self.__gui_manager.interpolate_points(self.__gui_manager.get_active_polygon_id(),
                                                      self.__gui_manager.get_active_model_id(),
                                                      self.__distance_current_value,
                                                      self.__combo_options[self.__current_combo_option])
            except InterpolationError as e:
                if e.code == 1:
                    self.__gui_manager.set_modal_text('Error', 'There is not enough points in the polygon to do'
                                                               ' the interpolation.')
                elif e.code == 2:
                    self.__gui_manager.set_modal_text('Error', 'Distance must be greater than 0 to do the '
                                                               'interpolation')
                elif e.code == 3:
                    self.__gui_manager.set_modal_text('Error', 'Model used for interpolation is not accepted by '
                                                               'the program.')
