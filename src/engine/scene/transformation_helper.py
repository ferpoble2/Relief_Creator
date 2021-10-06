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
File with the class TransformationHelper, class in charge of making transformation to the points of different models.
"""
from typing import List

import numpy as np
from scipy import interpolate as interpolate_scipy
from shapely.geometry.polygon import LineString, LinearRing as LinearRing, Polygon
from shapely.ops import triangulate
from shapely.vectorized import contains
from skimage.filters import gaussian as gaussian_filter

from src.utils import get_logger, interpolate, is_clockwise

log = get_logger(module='TRANSFORMATION_HELPER')


class TransformationHelper:
    """
    Helper class to execute different kind of transformation to the points of the maps.

    Mainly programmed using shapely and numpy as basis to be able to execute the different operations efficiently.
    """

    def __init__(self):
        """
        Constructor of the class.

        Do nothing.
        """
        pass

    def __delete_z_axis(self, list_of_points: list) -> list:
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

    # noinspection SpellCheckingInspection
    def __generate_mask(self, points_array: np.ndarray, polygon_points) -> np.ndarray:
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

    # noinspection PyShadowingNames,PyUnresolvedReferences
    def __get_bounding_box_indexes(self, points_array: np.ndarray, polygon: LinearRing) -> list:
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

    def __interpolate_nan(self, array_2d: np.ndarray, nan_mask: np.ndarray,
                          interpolation_type: str = 'linear') -> np.ndarray:
        """
        Interpolate the missing values from the array2d using scipy interpolation method.

        Args:
            array_2d: Array 2D with missing values to interpolate.
            nan_mask: Array 2D with a mask specifying where are located the nan values.
            interpolation_type: Type of the interpolation. (nearest, linear, cubic)

        Returns: Array interpolated.
        """
        log.debug('Interpolating nan')

        log.debug('Generating data arrays')
        # noinspection PyShadowingNames
        grid_x, grid_y = np.mgrid[:array_2d.shape[0], :array_2d.shape[1]]
        data = np.zeros((array_2d.shape[0], array_2d.shape[1], 3))
        data[:, :, 0] = grid_x
        data[:, :, 1] = grid_y
        data[:, :, 2] = array_2d

        # change shape of the data to an array of points
        nan_mask = nan_mask.reshape(-1)
        data = data.reshape((-1, 3))

        # select only points that have values and have a nan neighbour
        original_data = np.isnan(array_2d)
        shift_up = np.isnan(np.roll(array_2d, 1, axis=0))
        shift_down = np.isnan(np.roll(array_2d, -1, axis=0))
        shift_left = np.isnan(np.roll(array_2d, -1, axis=1))
        shift_right = np.isnan(np.roll(array_2d, 1, axis=1))
        pivots_points = ~original_data & (shift_up | shift_down | shift_left | shift_right)
        pivot_points_1d = pivots_points.reshape(-1)

        # select the points and their value to use as values for the interpolation
        points = data[pivot_points_1d][:, 0:2]
        values = data[pivot_points_1d][:, 2]

        # Deprecated code
        # Uses all the points of the matrix to interpolate. Too slow...
        # -------------------------------------------------------------
        # # noinspection PyShadowingNames
        # points = data[~nan_mask][:, 0:2]
        # # noinspection PyShadowingNames
        # values = data[~nan_mask][:, 2]

        points_to_interpolate = data[nan_mask][:, 0:2]

        log.debug('Initiated interpolate process using numpy')
        # noinspection PyShadowingNames
        y = interpolate_scipy.griddata(points, values, points_to_interpolate, method=interpolation_type)
        log.debug('Finished interpolation')

        data_nan_mask = data[nan_mask]
        data_nan_mask[:, 2] = y
        data[nan_mask] = data_nan_mask
        data = data[:, 2]
        data = data.reshape(array_2d.shape)
        log.debug('Ended nan interpolation')

        return data

    def apply_smoothing_over_area(self, internal_polygon_points: list,
                                  external_polygon_points: list,
                                  points_array: np.ndarray,
                                  heights: np.ndarray) -> np.ndarray:
        """
        Apply a smoothing algorithm in the area between the polygon and the external polygon.

        This method does not modify the original arrays.

        Args:
            points_array: Arrays with the coordinates of the points. must have shape (x,y,3)
            internal_polygon_points: Points of the internal polygon. [x1, y1, z1, x2, y2, z2, ...]
            external_polygon_points: Points of the external polygon. [x1, y1, z1, x2, y2, z2, ...]
            heights: Array with the height of the points. must have shape (x, y)

        Returns: Array with the new heights.
        """
        external_points_no_z_axis = self.__delete_z_axis(external_polygon_points)

        # bounding box
        # get the bounding box of the nan values
        min_x_index, max_x_index, min_y_index, max_y_index = self.__get_bounding_box_indexes(
            points_array,
            LinearRing(external_points_no_z_axis))

        # make a copy to not alter the original heights
        heights = heights.copy()

        # bounding box of the points and height (we need one extra pixel)
        points_cut = points_array[min_y_index:max_y_index, min_x_index:max_x_index, :]
        heights_cut = heights[min_y_index:max_y_index, min_x_index:max_x_index]

        # Apply laplace smoothing over one matrix
        new_heights = gaussian_filter(heights_cut)

        mask = self.__generate_mask(points_cut, internal_polygon_points)
        mask_external = self.__generate_mask(points_cut, external_polygon_points)
        mask_in_between = mask != mask_external

        heights_cut[mask_in_between] = new_heights[mask_in_between]

        heights[min_y_index:max_y_index, min_x_index:max_x_index] = heights_cut

        return heights

    def get_inside_polygon_triangulation(self, polygon_points: list, z_value: float = 0.5) -> list:
        """
        Get a list of floats representing the vertices of the triangles to cover the interior of the polygon.

        Args:
            z_value: Value to use as a third component of the vertices.
            polygon_points: Points of the polygon. (internal area should not be considered in the output)

        Returns: list with vertices of triangles.
        """

        # get the data clean
        polygon_points_no_z = self.__delete_z_axis(polygon_points)
        polygon = Polygon(polygon_points_no_z)

        # triangulate the coordinates
        triangulation = triangulate(polygon)
        to_return = []

        # clean the triangulation
        for triangle in triangulation:
            coords = list(zip(*triangle.exterior.coords.xy))

            line_1 = LineString([coords[0], coords[1]])
            line_2 = LineString([coords[1], coords[2]])
            line_3 = LineString([coords[2], coords[3]])

            if isinstance(polygon.intersection(line_1), LineString) and \
                    isinstance(polygon.intersection(line_2), LineString) and \
                    isinstance(polygon.intersection(line_3), LineString):
                to_return.append(coords[0][0])
                to_return.append(coords[0][1])
                to_return.append(z_value)

                to_return.append(coords[1][0])
                to_return.append(coords[1][1])
                to_return.append(z_value)

                to_return.append(coords[2][0])
                to_return.append(coords[2][1])
                to_return.append(z_value)

        return to_return

    def get_max_min_inside_polygon(self, points_array: np.ndarray, polygon_points: List[float],
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
        points_no_z_axis = self.__delete_z_axis(polygon_points)
        closed_polygon = LinearRing(points_no_z_axis)
        [min_x_index, max_x_index, min_y_index, max_y_index] = self.__get_bounding_box_indexes(points_array,
                                                                                               closed_polygon)

        points_array_cut = points_array[min_y_index:max_y_index, min_x_index:max_x_index, :]
        heights_cut = heights[min_y_index:max_y_index, min_x_index:max_x_index]

        flags = self.__generate_mask(points_array_cut, polygon_points)

        # return nan if no points are inside the polygon
        if len(heights_cut.reshape(-1)) == 0:
            return np.nan, np.nan

        maximum = np.nanmax(heights_cut[flags])
        minimum = np.nanmin(heights_cut[flags])

        return maximum, minimum

    def interpolate_points_external_to_polygon(self, points_array: np.ndarray, polygon_points: list,
                                               heights: np.ndarray, external_polygon_points: list,
                                               type_interpolation: str) -> np.ndarray:
        """
        Interpolate the points that are external to the polygon until a certain distance.

        Interpolation types are the followings:
            - linear
            - nearest
            - cubic

        Args:
            type_interpolation: Type of interpolation to use.
            external_polygon_points: List with the points of the external polygon. [x1, y1, z1, x2, y2, z2, ...]
            points_array: Points of the model. (shape must be (x, y, 3))
            polygon_points: List with the points of the polygon. [x1, y1, z1, x2, y2, z2, ...]
            heights: Array with the height of the points. must have shape (x, y)

        Returns: Array of heights with height of the points external to the polygon modified.
        """
        log.debug('Interpolate points external to polygon')
        external_points_no_z_axis = self.__delete_z_axis(external_polygon_points)

        # check if the points are already CW
        if is_clockwise(external_points_no_z_axis):  # points must be in CCW direction
            external_points_no_z_axis.reverse()

        # create a polygon external to the one proportionate
        exterior_polygon = LinearRing(external_points_no_z_axis)

        # get the bounding box of the nan values. Add/subtract 1 from every index to get one row/col of values before
        # the nan values.
        min_x_index, max_x_index, min_y_index, max_y_index = self.__get_bounding_box_indexes(points_array,
                                                                                             exterior_polygon)
        min_x_index -= 1
        max_x_index += 1
        min_y_index -= 1
        max_y_index += 1

        # copy the array to not modify the original
        heights = heights.copy()

        points_cut = points_array[min_y_index:max_y_index, min_x_index:max_x_index, :]
        heights_cut = heights[min_y_index:max_y_index, min_x_index:max_x_index]

        # generate a mask of the internal points
        log.debug('Generating masks')
        mask_external = self.__generate_mask(points_cut, external_polygon_points)
        mask_internal = self.__generate_mask(points_cut, polygon_points)

        # apply the logical operations
        in_between_mask = mask_external != mask_internal
        heights_cut[in_between_mask == True] = np.nan  # noqa

        # apply the interpolation algorithm from scipy
        log.debug('Interpolating using numpy')
        heights_cut = self.__interpolate_nan(heights_cut, in_between_mask, type_interpolation)
        heights[min_y_index:max_y_index, min_x_index:max_x_index] = heights_cut

        return heights

    def merge_matrices(self, first_matrix: np.ndarray, second_matrix: np.ndarray) -> np.ndarray:
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
