"""
File with the class ReliefTools. Class in charge of render the Relief tools inside another frame.
"""

import imgui

from src.utils import get_logger

log = get_logger(module="RELIEF_TOOLS")


class ReliefTools:
    """
    Class that render the ReliefTools inside another frame.
    """

    def __init__(self, gui_manager: 'GUIManager'):
        """
        Constructor of the class.
        """
        self.__gui_manager = gui_manager

        self.__combo_options = ["Linear", "Cubic", "Another One..."]
        self.__current_combo_option = 0

        self.__max_height_value = 0
        self.__min_height_value = 0

    def render(self) -> None:
        """
        Render the relief tools to modify the relief of the model.
        Returns: None
        """

        imgui.text('Relief Tools')

        clicked, self.__current_combo_option = imgui.combo(
            "Type of interpolation", self.__current_combo_option, self.__combo_options
        )

        imgui.input_float('Min Height', self.__min_height_value)
        imgui.input_float('Max Height', self.__max_height_value)

        if imgui.button('Change Height', -1):
            log.debug('Pressed button change height')
