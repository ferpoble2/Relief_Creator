"""
File with the class ReliefTools. Class in charge of render the Relief tools inside another frame.
"""

import imgui
import psutil
import os

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

    def render(self) -> None:
        """
        Render the relief tools to modify the relief of the model.
        Returns: None
        """

        imgui.text('Relief Tools')

        imgui.selectable('Linear')

        imgui.input_text('Max Height', '', 30)
        imgui.input_text('Min Height', '', 30)

        pass
