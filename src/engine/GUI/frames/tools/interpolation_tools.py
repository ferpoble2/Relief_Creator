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
File with the class InterpolationTools. Class in charge of render the Interpolation Tools inside another frame.
"""

from typing import TYPE_CHECKING

import imgui

from src.engine.scene.interpolation.cubic_interpolation import CubicInterpolation
from src.engine.scene.interpolation.linear_interpolation import LinearInterpolation
from src.engine.scene.interpolation.nearest_interpolation import NearestInterpolation
from src.engine.scene.interpolation.smooth_interpolation import SmoothInterpolation
from src.utils import get_logger

if TYPE_CHECKING:
    from engine.GUI.guimanager import GUIManager

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

        self.__combo_options = ['linear', 'nearest', 'cubic', 'smooth']
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

        if imgui.button('Preview Interpolation Area', -1):
            log.debug('Interpolation Area')
            self.__gui_manager.load_preview_interpolation_area(self.__distance_current_value)

        if imgui.button('Remove Preview', -1):
            log.debug('Delete preview')
            self.__gui_manager.remove_interpolation_preview(self.__gui_manager.get_active_polygon_id())

        if imgui.button('Interpolate', -1):
            log.debug('Interpolating points.')

            if self.__current_combo_option == 0:
                interpolation = LinearInterpolation(self.__gui_manager.get_active_model_id(),
                                                    self.__gui_manager.get_active_polygon_id(),
                                                    self.__distance_current_value)
                self.__gui_manager.interpolate_points(interpolation)

            elif self.__current_combo_option == 1:
                interpolation = NearestInterpolation(self.__gui_manager.get_active_model_id(),
                                                     self.__gui_manager.get_active_polygon_id(),
                                                     self.__distance_current_value)
                self.__gui_manager.interpolate_points(interpolation)

            elif self.__current_combo_option == 2:
                interpolation = CubicInterpolation(self.__gui_manager.get_active_model_id(),
                                                   self.__gui_manager.get_active_polygon_id(),
                                                   self.__distance_current_value)
                self.__gui_manager.interpolate_points(interpolation)

            elif self.__current_combo_option == 3:
                interpolation = SmoothInterpolation(self.__gui_manager.get_active_model_id(),
                                                    self.__gui_manager.get_active_polygon_id(),
                                                    self.__distance_current_value)
                self.__gui_manager.interpolate_points(interpolation)

            else:
                raise NotImplementedError('Interpolation method not implemented on the GUI.')
