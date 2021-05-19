"""
File with the class TransformationHelper, class in charge of making transformation to the points of different models.
"""
import numpy as np
from shapely.geometry.polygon import LinearRing as LinearRing
from shapely.geometry.polygon import Polygon, LineString
from shapely.ops import triangulate
from typing import List
from matplotlib import path
from scipy import interpolate as interpolate_scipy
from scipy.spatial.distance import cdist
from skimage.filters import gaussian as gaussian_filter

from src.utils import interpolate
from src.utils import is_clockwise
from src.utils import get_logger

log = get_logger(module='TRANSFORMATION_HELPER')


class TransformationHelper:
    """
    Class in charge of executing transformation to different models in the scene.
    """

    def __init__(self):
        """
        Constructor of the class.
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

    def __generate_mask(self, points_array: np.ndarray, polygon_points) -> np.ndarray:
        """
        Generate a mask of the points that are inside the specified polygon.

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
        # get a mask for the points inside
        xv = points_array[:, :, 0]
        yv = points_array[:, :, 1]
        # noinspection PyTypeChecker
        p = path.Path(points_xy)

        # noinspection PyTypeChecker
        flags = p.contains_points(np.hstack((xv.flatten()[:, np.newaxis], yv.flatten()[:, np.newaxis])))
        flags = flags.reshape(xv.shape)
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

    # noinspection PyUnresolvedReferences
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

        nan_mask = nan_mask.reshape(-1)
        data = data.reshape((-1, 3))

        # noinspection PyShadowingNames
        points = data[~nan_mask][:, 0:2]
        # noinspection PyShadowingNames
        values = data[~nan_mask][:, 2]

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

    def __generate_filter_masks(self,
                                points_to_modify: np.ndarray,
                                points_array: np.ndarray,
                                height_array: np.ndarray,
                                filter_data: list) -> np.ndarray:
        """
        Generates a mask that indicates which data to use for the interpolation.
        Requires and initial mask that indicates the points that can be filtered from the one who do not.

        Filter are expected to be received in a list with the following format [(filter_name, arguments),...].
        The list of accepted filters and its arguments are as follows:
            height_less_than: int
            height_greater_than: int
            is_in: List[float]
            is_not_in: List[float]

        Args:
            points_to_modify: Initial mask in which to apply the filters on.
            points_array: Array with the points and their position.
            height_array: Array with the height of the points.
            filter_data: Filters to use to generate the masks.

        Returns: Mask with the filters applied over it.
        """
        mask_modified = points_to_modify.copy()
        for filter_obj in filter_data:
            filter_name = filter_obj[0]
            filter_arguments = filter_obj[1]

            if filter_name == 'height_less_than':  # arguments: int
                indices = np.where(height_array > filter_arguments)
                mask_modified[indices] = False

            elif filter_name == 'height_greater_than':  # arguments: int
                indices = np.where(height_array < filter_arguments)
                mask_modified[indices] = False

            elif filter_name == 'is_in':    # arguments: list[float]
                polygon_mask = self.__generate_mask(points_array, filter_arguments) & points_to_modify
                indices = np.where(polygon_mask == True)
                mask_modified[indices] = True

            elif filter_name == 'is_not_in':
                polygon_mask = self.__generate_mask(points_array, filter_arguments) & points_to_modify
                indices = np.where(polygon_mask == True)
                mask_modified[indices] = False

            else:
                raise NotImplementedError(f'Functionality to generate the mask of the filter {filter_name} '
                                          f'not implemented.')

        return mask_modified

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

    def modify_points_inside_polygon_linear(self, points_array: np.ndarray,
                                            height: np.ndarray,
                                            polygon_points: List[float],
                                            new_max_height: float,
                                            new_min_height: float,
                                            filter_data: list = None) -> np.ndarray:
        """
        Modify the points that are inside the polygon changing their height using a linear interpolation
        given the new specified height.

        Args:
            filter_data: Filters to use on the transformation to apply. List must have format [(filter_id, args),...].
            height: Array with the height of the points. must have shape (x, y)
            points_array: Points to modify (numpy array of points), must have shape (x, y, 3)
            polygon_points: List of points in the polygon. [x1, y1, z1, x2, y2, z2, ...]
            new_max_height: New height to interpolate the points
            new_min_height: New height to interpolate the points

        Returns: numpy.array with the new points
        """
        if filter_data is None:
            filter_data = []

        # generate polygon and get the bounding box of the indices.
        points_no_z_axis = self.__delete_z_axis(polygon_points)
        closed_polygon = LinearRing(points_no_z_axis)
        [min_x_index, max_x_index, min_y_index, max_y_index] = self.__get_bounding_box_indexes(points_array,
                                                                                               closed_polygon)

        points_array_cut = points_array[min_y_index:max_y_index, min_x_index:max_x_index, :]
        height_cut = height[min_y_index:max_y_index, min_x_index:max_x_index]

        log.debug('Generating mask')
        flags = self.__generate_mask(points_array_cut, polygon_points)
        log.debug('Mask generated')

        # get the masks of the filters and apply them
        filtered_flags = self.__generate_filter_masks(flags,
                                                      points_array_cut,
                                                      height_cut,
                                                      filter_data)

        # modify the height linearly
        current_min_height = np.min(height_cut[filtered_flags])
        current_max_height = np.max(height_cut[filtered_flags])

        new_height = interpolate(height_cut[filtered_flags], current_min_height, current_max_height, new_min_height,
                                 new_max_height,
                                 False)

        height_cut[filtered_flags] = new_height
        height[min_y_index:max_y_index, min_x_index:max_x_index] = height_cut
        return height

    def interpolate_points_external_to_polygon(self, points_array: np.ndarray, polygon_points: list,
                                               heights: np.ndarray, external_polygon_points: list,
                                               type_interpolation: str) -> np.ndarray:
        """
        Interpolate the points that are external to the polygon until a certain distance.

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

        # get the bounding box of the nan values
        min_x_index, max_x_index, min_y_index, max_y_index = self.__get_bounding_box_indexes(points_array,
                                                                                             exterior_polygon)

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

    def get_interpolation_zone_triangulation(self, internal_polygon_points: list,
                                             external_polygon_points: list,
                                             distance: float,
                                             z_value: float = 0.5):
        """
        Get the vertices of the triangles that cover the interpolation area between two polygons.

        Args:
            internal_polygon_points: Points of the internal polygon to use. [x1, y1, z1, x2, y2, z2, ...]
            external_polygon_points: Points of the external polygon to use. [x1, y1, z1, x2, y2, z2, ...]
            distance: Distance used to calculate the external polygon.
            z_value: Default value for the Z-axis value for the points.

        Returns: list with the points of the triangles that cover the interpolation area.
        """
        new_points_internal = self.__insert_redundant_points(distance, internal_polygon_points)
        new_points_external = self.__insert_redundant_points(distance, external_polygon_points)

        polygon_internal = Polygon(new_points_internal)
        polygon_internal_coords = list(zip(*polygon_internal.exterior.coords.xy))

        polygon_external = Polygon(new_points_external)
        polygon_external_coords = list(zip(*polygon_external.exterior.coords.xy))

        triangulation = triangulate(Polygon(new_points_internal + new_points_external))
        to_return = []

        # clean the triangulation
        for triangle in triangulation:
            coords = list(zip(*triangle.exterior.coords.xy))

            # do not add if triangle is completely external
            if coords[0] in polygon_external_coords and coords[1] in polygon_external_coords and \
                    coords[2] in polygon_external_coords:
                should_add = False

            # do not add if triangle is completely internal
            elif coords[0] in polygon_internal_coords and coords[1] in polygon_internal_coords and \
                    coords[2] in polygon_internal_coords:
                should_add = False

                line1 = LineString([(coords[0][0], coords[0][1]),
                                    (coords[1][0], coords[1][1])])
                line2 = LineString([(coords[1][0], coords[1][1]),
                                    (coords[2][0], coords[2][1])])
                line3 = LineString([(coords[2][0], coords[2][1]),
                                    (coords[3][0], coords[3][1])])

                # but add it if it is external but with internal vertices (U-shaped polygon)
                if not (isinstance(polygon_internal.intersection(line1), LineString) and
                        isinstance(polygon_internal.intersection(line2), LineString) and
                        isinstance(polygon_internal.intersection(line3), LineString)):
                    should_add = True

            # in any other case, add it.
            else:
                should_add = True

            if should_add:
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

    def __insert_redundant_points(self, distance: float, polygon_points: list):
        """
        Insert redundant points in a line of the polygon if the line is longer than the specified distance.

        Args:
            distance: Distance to use as a limit to check if insert or not new points.
            polygon_points: List of original points of the polygon. [[x1,y1],[x2,y2],...]

        Returns: List of new points of the polygon. [[x1,y1],[x2,y2],...]
        """

        # delete repeated point at the end.
        if polygon_points[-3:] == polygon_points[:3]:
            polygon_points.pop()
            polygon_points.pop()
            polygon_points.pop()

        external_polygon_points_no_z = self.__delete_z_axis(polygon_points)
        external_polygon_points_no_z_offset = external_polygon_points_no_z[1:] + external_polygon_points_no_z[:1]
        distance_polygon_points_external = cdist(external_polygon_points_no_z,
                                                 external_polygon_points_no_z_offset,
                                                 'euclidean')
        new_points_external = []
        for point, next_point, index in zip(external_polygon_points_no_z,
                                            external_polygon_points_no_z_offset,
                                            range(len(external_polygon_points_no_z))):
            new_points_external.append(point)
            if distance_polygon_points_external[index][index] > distance:
                number_of_divisions = int(distance_polygon_points_external[index][index] / distance)

                for division in range(1, number_of_divisions):
                    x = point[0] + ((next_point[0] - point[0]) / number_of_divisions) * division
                    y = point[1] + ((next_point[1] - point[1]) / number_of_divisions) * division
                    new_points_external.append([x, y])

        return new_points_external

    def get_max_min_inside_polygon(self, points_array: np.ndarray, polygon_points: List[float],
                                   heights: np.ndarray) -> tuple:
        """
        Extract the maximum and minimum value of the points that are inside the polygon.

        Args:
            points_array: Points of the model. (shape must be (x, y, 3))
            polygon_points: List with the points of the polygon. [x1, y1, z1, x2, y2, z2, ...]
            heights: height: Array with the height of the points. must have shape (x, y)

        Returns: Tuple with the maximum and minimum value
        """
        points_no_z_axis = self.__delete_z_axis(polygon_points)
        closed_polygon = LinearRing(points_no_z_axis)
        [min_x_index, max_x_index, min_y_index, max_y_index] = self.__get_bounding_box_indexes(points_array,
                                                                                               closed_polygon)

        points_array_cut = points_array[min_y_index:max_y_index, min_x_index:max_x_index, :]
        heights_cut = heights[min_y_index:max_y_index, min_x_index:max_x_index]

        flags = self.__generate_mask(points_array_cut, polygon_points)

        maximum = np.max(heights_cut[flags])
        minimum = np.min(heights_cut[flags])

        return maximum, minimum

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
