#  BEGIN GPL LICENSE BLOCK
#
#      This program is free software: you can redistribute it and/or modify
#      it under the terms of the GNU General Public License as published by
#      the Free Software Foundation, either version 3 of the License, or
#      (at your option) any later version.
#
#      This program is distributed in the hope that it will be useful,
#      but WITHOUT ANY WARRANTY; without even the implied warranty of
#      MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#      GNU General Public License for more details.
#
#      You should have received a copy of the GNU General Public License
#      along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
#  END GPL LICENSE BLOCK

"""
Utility module that defines different geometrical operations.
"""
from typing import List

import numpy as np
from shapely.geometry.polygon import LinearRing as LinearRing, Polygon
from shapely.vectorized import contains


def delete_z_axis(list_of_points: List[float]) -> list:
    """
    Delete the third component of a list of points, returning a list only with the first two components of
    each point.

    input: [a.x,a.y,a.z,b.x,b.y,b.z,c.x,...]
    output: [[a.x,a.y],[b.x,b.y],[c.x,...]

    Args:
        list_of_points: List of points to use

    Returns: List with the points without the third component
    """
    new_list = []
    pair_used = []
    for component_ind in range(len(list_of_points)):
        if component_ind % 3 == 0:
            pair_used.append(list_of_points[component_ind])
        elif component_ind % 3 == 1:
            pair_used.append(list_of_points[component_ind])
        elif component_ind % 3 == 2:
            new_list.append(pair_used)
            pair_used = []
    return new_list


def get_bounding_box_indexes(points_array: np.ndarray, polygon: LinearRing) -> list:
    """
    Get the indices to use in the matrix to get only the values of the matrix that are inside the bounding
    box of the polygon.

    Args:
        points_array: Array 2D with shape (x,y,3) with the values of the points.
        polygon: Polygon to use to get the bounding box.

    Returns: [min_x, max_x, min_y, max_y]
    """

    # get the bounding box of the nan values
    (minx, miny, max_x, maxy) = polygon.bounds
    min_x_index = np.searchsorted(points_array[0, :, 0], minx)
    max_x_index = np.searchsorted(points_array[0, :, 0], max_x)

    min_y_index = np.searchsorted(points_array[:, 0, 1], miny)
    max_y_index = np.searchsorted(points_array[:, 0, 1], maxy)

    return [min_x_index, max_x_index, min_y_index, max_y_index]


def generate_mask(points_array: np.ndarray, polygon_points) -> np.ndarray:
    """
    Generate a mask of the points that are inside the specified polygon. This method does not considerate the
    points that are on the polygon, returning false in case they exists.

    Mask is a numpy array with booleans representing if the point is inside the polygon or not.

    Args:
        points_array: Numpy array with the points (shape must be (x, y, 3))
        polygon_points: List with the points of the polygon. [x1, y1, z1, x2, y2, z2, ...]

    Returns: Numpy array with booleans indicating if the points are inside the polygon or not.
    """

    # generate the polygon
    points_xy = []
    for point_ind in range(len(polygon_points)):
        if point_ind % 3 == 0:
            points_xy.append((polygon_points[point_ind], polygon_points[point_ind + 1]))

    flags = contains(Polygon(points_xy), points_array[:, :, 0], points_array[:, :, 1])
    return flags
