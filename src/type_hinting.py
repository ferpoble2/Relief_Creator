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
File that do fake imports of the classes used in type hinting to make them available for the
pycharm linting.

usage:

from src.type_hinting import *

or

from src.type_hinting import some_class
"""

# noinspection PyUnreachableCode
if False:
    from src.engine.GUI.guimanager import GUIManager
    from src.engine.engine import Engine
    from src.engine.scene.scene import Scene
    from src.engine.scene.model.map2dmodel import Map2DModel
    from src.program.program import Program

    import numpy as np
