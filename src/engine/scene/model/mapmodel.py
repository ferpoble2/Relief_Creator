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
File with the abstract class MapModel, abstract class in charge of the definition of common methods between maps models.
"""

from typing import Union

import numpy as np

from src.engine.scene.model.model import Model


class MapModel(Model):
    """
    Abstract class for the map models.
    """

    # noinspection PyUnresolvedReferences
    def _get_index_closest_value(self, list_to_evaluate: Union[list, np.ndarray], value: float) -> int:
        """
        Get the index of the closest element in the array to the value.

        Args:
            list_to_evaluate: List with numeric elements
            value: Value to search for

        Returns: Index of the closest value in the array.
        """
        return int(np.argmin(np.abs(np.array(list_to_evaluate) - value)))

    def _get_vertex_index(self, x_pos: int, y_pos: int, x_value_array: np.ndarray) -> int:
        """
        Get the vertex index in the buffer given the x and y position.

        The positions are given as in a cartesian plane.
        The 0,0 exist.

        Args:
            x_pos: Position X of the vertex
            y_pos: Position Y of the vertex

        Returns: Index of the vertex in the buffer.
        """
        return y_pos * len(x_value_array) + x_pos

    def _generate_index_list(self,
                             step_x: int,
                             step_y: int,
                             x_value_array: np.ndarray,
                             y_value_array: np.ndarray,
                             left_coordinate: float = -180,
                             right_coordinate: float = 180,
                             top_coordinate: float = 90,
                             bottom_coordinate: float = -90) -> np.ndarray:
        """
        Generate an index list given an already loaded list of vertices.

        Vertices are expected to be given as in the output of the __generate_vertices_list method.

        The coordinates values are used to generate the index of just a part of the total of the vertices.

        Args:
            left_coordinate: Left coordinate to cut the map.
            right_coordinate: Right coordinate to cut the map.
            top_coordinate: Top coordinate to cut the map.
            bottom_coordinate: Bottom coordinate to cut the map.
            step_x: Number of vertices in the x axis
            step_y: Number of elements in the y axis
            x_value_array: Values used in the x-axis
            y_value_array: Values used in the y-axis

        Returns: List of index
        """

        step_x = max(1, step_x)
        step_y = max(1, step_y)

        # Get the index of the vertices to generate the indexes
        # -----------------------------------------------------
        index_minimum_x = self._get_index_closest_value(x_value_array, left_coordinate)
        index_maximum_x = self._get_index_closest_value(x_value_array, right_coordinate)
        index_minimum_y = self._get_index_closest_value(y_value_array, bottom_coordinate)
        index_maximum_y = self._get_index_closest_value(y_value_array, top_coordinate)

        # Sort the result from the calculus
        # ---------------------------------
        new_index_minimum_y = min(index_maximum_y, index_minimum_y)
        new_index_maximum_y = max(index_maximum_y, index_minimum_y)
        new_index_maximum_x = max(index_maximum_x, index_minimum_x)
        new_index_minimum_x = min(index_maximum_x, index_minimum_x)

        # Assign the correct values to the variables
        # ------------------------------------------
        index_minimum_y = new_index_minimum_y
        index_maximum_y = new_index_maximum_y
        index_maximum_x = new_index_maximum_x
        index_minimum_x = new_index_minimum_x

        # calculate the indices to add to the program using numpy
        # -------------------------------------------------------
        cushion_rows = step_y - (index_maximum_y - index_minimum_y) % step_y + 1
        cushion_cols = step_x - (index_maximum_x - index_minimum_x) % step_x + 1

        rows = range(len(y_value_array))[index_minimum_y:index_maximum_y + cushion_rows:step_y]
        cols = range(len(x_value_array))[index_minimum_x:index_maximum_x + cushion_cols:step_x]
        len_rows = len(rows)
        len_cols = len(cols)

        rows = np.tile(np.array(rows), (len_cols, 1)).transpose()
        cols = np.tile(np.array(cols), (len_rows, 1))

        other_cols = cols[:-1, :-1]
        other_rows = rows[:-1, :-1]

        # first part of the triangles
        # ---------------------------

        # noinspection PyTypeChecker
        index_1: np.ndarray = self._get_vertex_index(other_cols, other_rows, x_value_array)
        # noinspection PyTypeChecker
        index_2: np.ndarray = self._get_vertex_index(other_cols + step_x, other_rows, x_value_array)
        # noinspection PyTypeChecker
        index_3: np.ndarray = self._get_vertex_index(other_cols, other_rows + step_y, x_value_array)

        index_1 = index_1.reshape(-1)
        index_2 = index_2.reshape(-1)
        index_3 = index_3.reshape(-1)

        # second part of the triangles
        # ---------------------------
        # noinspection PyTypeChecker
        index_4: np.ndarray = self._get_vertex_index(other_cols + step_x, other_rows, x_value_array)
        # noinspection PyTypeChecker
        index_5: np.ndarray = self._get_vertex_index(other_cols + step_x, other_rows + step_y, x_value_array)
        # noinspection PyTypeChecker
        index_6: np.ndarray = self._get_vertex_index(other_cols, other_rows + step_y, x_value_array)

        index_4 = index_4.reshape(-1)
        index_5 = index_5.reshape(-1)
        index_6 = index_6.reshape(-1)

        indices = np.zeros((len(index_1), 6))
        indices[:, 0] = index_1
        indices[:, 1] = index_2
        indices[:, 2] = index_3
        indices[:, 3] = index_4
        indices[:, 4] = index_5
        indices[:, 5] = index_6
        indices = indices.reshape(-1).astype(np.uint32)

        return indices
