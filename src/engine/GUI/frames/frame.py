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
Main Frame class for the others elements to use.
"""
from src.type_hinting import *


class Frame:
    """
    Class to manager the frame behaviour. New frames must be children of this class.
    """

    def __init__(self, gui_manager: 'GUIManager'):
        """
        Constructor of the class.
        """
        self._position = [100, 100]
        self._GUI_manager = gui_manager

    def change_position(self, new_position: list) -> None:
        """
        Change the position of the frame in the screen. Only works properly when fixed_position is set to True.
        Args:
            new_position: New position where to put the frame. ([x_pos, y_pos])
        Returns: None
        """
        self._position = new_position

    def get_position(self) -> list:
        """
        Get the position of the frame.
        Returns: list with the position of the frame.
        """
        return self._position

    def add_new_polygon(self, polygon_id) -> None:
        """
        Function to call to add a new polygon into the frame.

        Must be defined in child classes.

        Args:
            polygon_id: ID of the polygon.

        Returns: None
        """
        pass

    def render(self) -> None:
        """
        Draw the frames on the screen.

        Note: Due to the implementation of imgui, it is recommendable to implement here all the logic related to the
        windows that the program will show (imgui.begin(...)/imgui.end()) and to program all the logic related to the
        popups to the post_render method.

        Returns: None
        """
        raise NotImplementedError("Render method not implemented.")

    def post_render(self) -> None:
        """
        Logic to execute after the rendering process of all the frames.

        Note: Due to the implementation of the module imgui, it is recommendable to implement all the logic
        related to the popup in this post-render method to make the probability of bugs smaller.

        Returns: None
        """
        pass
