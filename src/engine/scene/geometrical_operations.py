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
from scipy import interpolate
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


def get_bounding_box_indexes(points_array: np.ndarray, polygon: LinearRing) -> list[int]:
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


def merge_matrices(first_matrix: np.ndarray, second_matrix: np.ndarray) -> np.ndarray:
    """
    Merge the values of the matrices.

    Set the values of the second matrix on the cells where the first matrix has nan values. Both matrices must
    be of the same shape.

    The values of the proportioned matrices does not change. A new matrix is generated as result of this method.

    Args:
        first_matrix: Main matrix to use for the merge.
        second_matrix: Second matrix to use for the merge.

    Returns: Matrix that use the values of the first matrix and the second matrix.
    """
    assert first_matrix.shape == second_matrix.shape, "Matrices are not of the same shape."

    new_matrix = np.zeros(first_matrix.shape)
    new_matrix[:] = first_matrix[:]
    new_matrix[np.isnan(first_matrix)] = second_matrix[np.isnan(first_matrix)]

    return new_matrix


def get_max_min_inside_polygon(points_array: np.ndarray,
                               polygon_points: List[float],
                               heights: np.ndarray) -> tuple:
    """
    Extract the maximum and minimum value of the points that are inside the polygon.

    If no points are inside the polygon, then numpy.nan is returned as maximum and minimum values.

    Args:
        points_array: Points of the model. (shape must be (x, y, 3))
        polygon_points: List with the points of the polygon. [x1, y1, z1, x2, y2, z2, ...]
        heights: height: Array with the height of the points. must have shape (x, y)

    Returns: Tuple with the maximum and minimum value (max, min).
    """
    points_no_z_axis = delete_z_axis(polygon_points)
    closed_polygon = LinearRing(points_no_z_axis)
    [min_x_index, max_x_index, min_y_index, max_y_index] = get_bounding_box_indexes(points_array,
                                                                                    closed_polygon)

    points_array_cut = points_array[min_y_index:max_y_index, min_x_index:max_x_index, :]
    heights_cut = heights[min_y_index:max_y_index, min_x_index:max_x_index]

    flags = generate_mask(points_array_cut, polygon_points)

    # return nan if no points are inside the polygon
    if len(heights_cut.reshape(-1)) == 0:
        return np.nan, np.nan

    maximum = np.nanmax(heights_cut[flags])
    minimum = np.nanmin(heights_cut[flags])

    return maximum, minimum


def get_external_polygon_points(polygon_points: List[float],
                                distance: float,
                                default_z_value: float = 0.5) -> List[float]:
    """
    Calculate the external polygon at a given distance from the specified polygon.

    Args:
        polygon_points: List of points of the polygon. [x1, y1, z1, x2, y2, z2, ...]
        distance: Distance to use to get the external polygon.
        default_z_value: Value to use in the z-axis of the external polygon points.

    Returns:
        List of points of the external polygon. [x1, y1, z1, x2, y2, z2, ...]
    """
    # Delete the z-axis value from the points
    # ---------------------------------------
    new_list = delete_z_axis(polygon_points)

    # Get the external polygon
    # ------------------------
    polygon_shapely = Polygon(new_list)
    external_polygon = polygon_shapely.buffer(distance).exterior

    # Get the coordinates and create a new list
    # -----------------------------------------
    x_coords, y_coords = external_polygon.xy
    polygon_exterior = []
    for x_coordinate, y_coordinate in zip(x_coords, y_coords):
        polygon_exterior.append(x_coordinate)
        polygon_exterior.append(y_coordinate)
        polygon_exterior.append(default_z_value)

    return polygon_exterior


def interpolate_nan(array_2d: np.ndarray,
                    nan_mask: np.ndarray,
                    interpolation_type: str = 'linear') -> np.ndarray:
    """
    Interpolate the missing values from the array2d using scipy interpolation method.

    Args:
        array_2d: Array 2D with missing values to interpolate.
        nan_mask: Array 2D with a mask specifying where are located the nan values.
        interpolation_type: Type of the interpolation. (nearest, linear, cubic)

    Returns: Array interpolated.
    """
    # noinspection PyShadowingNames
    grid_x, grid_y = np.mgrid[:array_2d.shape[0], :array_2d.shape[1]]
    data = np.zeros((array_2d.shape[0], array_2d.shape[1], 3))
    data[:, :, 0] = grid_x
    data[:, :, 1] = grid_y
    data[:, :, 2] = array_2d

    # Change shape of the data to an array of points
    # ----------------------------------------------
    nan_mask = nan_mask.reshape(-1)
    data = data.reshape((-1, 3))

    # Select only points that have values and have a nan neighbour
    # ------------------------------------------------------------
    original_data = np.isnan(array_2d)
    shift_up = np.isnan(np.roll(array_2d, 1, axis=0))
    shift_down = np.isnan(np.roll(array_2d, -1, axis=0))
    shift_left = np.isnan(np.roll(array_2d, -1, axis=1))
    shift_right = np.isnan(np.roll(array_2d, 1, axis=1))
    pivots_points = ~original_data & (shift_up | shift_down | shift_left | shift_right)
    pivot_points_1d = pivots_points.reshape(-1)

    # Select the points and their value to use as values for the interpolation
    # ------------------------------------------------------------------------
    points = data[pivot_points_1d][:, 0:2]
    values = data[pivot_points_1d][:, 2]

    points_to_interpolate = data[nan_mask][:, 0:2]
    if len(points_to_interpolate) == 0:
        return array_2d  # Do nothing if there is no points to interpolate

    if len(points) == 0:
        return array_2d  # Do nothing if there is no points to use as pivot

    # Interpolate values
    # ------------------
    # noinspection PyShadowingNames
    y = interpolate.griddata(points, values, points_to_interpolate, method=interpolation_type)

    # Modify the values of the data
    # -----------------------------
    data_nan_mask = data[nan_mask]
    data_nan_mask[:, 2] = y
    data[nan_mask] = data_nan_mask
    data = data[:, 2]
    data = data.reshape(array_2d.shape)

    return data
