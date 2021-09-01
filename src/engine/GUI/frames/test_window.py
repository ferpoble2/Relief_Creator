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
Test frame for the GUI (default for imgui).

The test frame is the one proportionate by IMGUI that shows all the possible things that can be done with IMGUI.
"""

import imgui

from src.engine.GUI.frames.frame import Frame
from src.utils import get_logger

log = get_logger(module="TEST WINDOW")


class TestWindow(Frame):
    """
    Class that render the test_window of imgui.

    This window contains all the possible frames and options that can be used with IMGUI.
    """

    def render(self) -> None:
        """
        Render the test window on the application.
        Returns: None
        """
        imgui.show_test_window()
