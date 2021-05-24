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
File with utils decimation algorithms to apply to 2D data.
"""

import numpy as np


def simple_decimation(x: np.ndarray, y: np.ndarray, z: np.ndarray, n_rows: int, n_cols: int) -> (list, list, list):
    """
    Function to decimate a two dimensional grid in a simple way. Take one element from every column/row with a step
    calculated to reach the final n_rows/n_cols.

    Don't decimate if there is less values than the number specified.

    Args:
        x: Grid values in the x axis. (1D array)
        y: Grid values in the y axis. (1D array)
        z: Grid values. (2D array)
        n_rows: Final number of rows to get.
        n_cols: Final number of cols to get.

    Returns: x, y, z New values of the grid with the data decimated.

    """

    # get the length of the matrix
    x_len = len(x)
    y_len = len(y)

    step_x = 1
    step_y = 1

    if x_len > n_rows:
        step_x = int(x_len / n_cols)
        step_x = max(step_x, 1)

    if y_len > n_cols:
        step_y = int(y_len / n_rows)
        step_y = max(step_y, 1)

    x = x[::step_x]
    y = y[::step_y]
    z = z[::step_y, ::step_x]

    return x, y, z
