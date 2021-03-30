"""
File with the class TransformationHelper, class in charge of making transformation to the points of different models.
"""
import numpy as np
from shapely.geometry.polygon import LinearRing as LinearRing
from typing import List
from matplotlib import path
from scipy import interpolate as interpolate_scipy

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
        grid_x, grid_y = np.mgrid[:array_2d.shape[0], :array_2d.shape[1]]
        data = np.zeros((array_2d.shape[0], array_2d.shape[1], 3))
        data[:, :, 0] = grid_x
        data[:, :, 1] = grid_y
        data[:, :, 2] = array_2d

        nan_mask = nan_mask.reshape(-1)
        data = data.reshape((-1, 3))

        points = data[~nan_mask][:, 0:2]
        values = data[~nan_mask][:, 2]

        points_to_interpolate = data[nan_mask][:, 0:2]

        log.debug('Initiated interpolate process using numpy')
        y = interpolate_scipy.griddata(points, values, points_to_interpolate, method=interpolation_type)
        log.debug('Finished interpolation')

        data_nan_mask = data[nan_mask]
        data_nan_mask[:, 2] = y
        data[nan_mask] = data_nan_mask
        data = data[:, 2]
        data = data.reshape(array_2d.shape)
        log.debug('Ended nan interpolation')

        return data

    def modify_points_inside_polygon_linear(self, points_array: np.ndarray,
                                            height: np.ndarray,
                                            polygon_points: List[float],
                                            new_max_height: float,
                                            new_min_height: float) -> np.ndarray:
        """
        Modify the points that are inside the polygon changing their height using a linear interpolation
        given the new specified height.

        Args:
            height: Array with the height of the points. must have shape (x, y)
            points_array: Points to modify (numpy array of points), must have shape (x, y, 3)
            polygon_points: List of points in the polygon. [x1, y1, z1, x2, y2, z2, ...]
            new_max_height: New height to interpolate the points
            new_min_height: New height to interpolate the points

        Returns: numpy.array with the new points
        """

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

        # modify the height linearly
        current_min_height = np.min(height_cut[flags])
        current_max_height = np.max(height_cut[flags])

        new_height = interpolate(height_cut[flags], current_min_height, current_max_height, new_min_height,
                                 new_max_height,
                                 False)

        height_cut[flags] = new_height
        height[min_y_index:max_y_index, min_x_index:max_x_index] = height_cut
        return height

    def interpolate_points_external_to_polygon(self, points_array: np.ndarray, polygon_points: list,
                                               heights: np.ndarray, distance: float) -> np.ndarray:
        """
        Interpolate the points that are external to the polygon until a certain distance.

        Args:
            distance: Limit distance to interpolate the points from.
            points_array: Points of the model. (shape must be (x, y, 3))
            polygon_points: List with the points of the polygon. [x1, y1, z1, x2, y2, z2, ...]
            heights: Array with the height of the points. must have shape (x, y)

        Returns: Array of heights with height of the points external to the polygon modified.
        """
        log.debug('Interpolate points external to polygon')

        points_no_z_axis = self.__delete_z_axis(polygon_points)

        # check if the points are already CW
        if is_clockwise(points_no_z_axis):  # points must be in CCW direction
            points_no_z_axis.reverse()

        # create a polygon external to the one proportionate
        closed_polygon = LinearRing(points_no_z_axis)
        exterior_polygon = closed_polygon.buffer(distance).exterior

        x_coords, y_coords = exterior_polygon.xy
        polygon_exterior = []

        for x_coordinate, y_coordinate in zip(x_coords, y_coords):
            polygon_exterior.append(x_coordinate)
            polygon_exterior.append(y_coordinate)
            polygon_exterior.append(0.5)

        # get the bounding box of the nan values
        min_x_index, max_x_index, min_y_index, max_y_index = self.__get_bounding_box_indexes(points_array,
                                                                                             exterior_polygon)

        points_cut = points_array[min_y_index:max_y_index, min_x_index:max_x_index, :]
        heights_cut = heights[min_y_index:max_y_index, min_x_index:max_x_index]

        # generate a mask of the internal points
        log.debug('Generating masks')
        mask_external = self.__generate_mask(points_cut, polygon_exterior)
        mask_internal = self.__generate_mask(points_cut, polygon_points)

        # apply the logical operations
        in_between_mask = mask_external != mask_internal
        heights_cut[in_between_mask == True] = np.nan  # noqa

        # apply the interpolation algorithm from scipy
        log.debug('Interpolating using numpy')
        heights_cut = self.__interpolate_nan(heights_cut, in_between_mask)
        heights[min_y_index:max_y_index, min_x_index:max_x_index] = heights_cut

        return heights

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


if __name__ == '__main__':

    # noinspection PyUnreachableCode
    if False:
        points_2d = [[0, 0], [0, 1], [0, 2], [1, 1], [1, 0]]

        # check if the points are already CW
        if is_clockwise(points_2d):  # points must be in CCW direction
            points_2d.reverse()

        linear_ring = LinearRing(points_2d)

        points_2d.append(points_2d[0])  # make it closed
        linear_ring2 = linear_ring.buffer(8)

        import matplotlib.pyplot as plt

        exterior = linear_ring2.exterior

        x, y = linear_ring.xy
        x2, y2 = exterior.xy

        plt.plot(x, y, color='red')
        plt.plot(x2, y2, color='green')
        plt.show()

    import numpy as np
    from scipy import interpolate
    import matplotlib.pyplot as plt

    #
    # Let's create some random  data
    array = np.random.random_integers(0, 10, (100, 100)).astype(float)
    array[:, :] = 10
    array[0:10, :] = 100
    array[:, 0:10] = 100
    array[10:70, 10:70] = np.nan

    array[80, 80:90] = np.nan
    array[80:90, 90] = np.nan
    plt.imshow(array)
    plt.show()

    # x = np.array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
    # y = np.array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
    #
    # GD1 = interpolate.interp2d(x, y, array)
    #
    # Z = GD1(y, x)

    # def nan_helper(y):
    #     """Helper to handle indices and logical indices of NaNs.
    #
    #     Input:
    #         - y, 1d numpy array with possible NaNs
    #     Output:
    #         - nans, logical indices of NaNs
    #         - index, a function, with signature indices= index(logical_indices),
    #           to convert logical indices of NaNs to 'equivalent' indices
    #     Example:
    #         >>> # linear interpolation of NaNs
    #         >>> nans, x= nan_helper(y)
    #         >>> y[nans]= np.interp(x(nans), x(~nans), y[~nans])
    #     """
    #
    #     return np.isnan(y), lambda z: z.nonzero()[0]
    #
    # y = array
    # nans, x = nan_helper(y)
    # y[nans] = np.interp(x(nans), x(~nans), y[~nans])

    grid_x, grid_y = np.mgrid[10:70, 10:70]
    points = []
    values = []

    for row in range(len(array)):
        for col in range(len(array[0])):
            if not np.isnan(array[row][col]):
                points.append([col, row])
                values.append(array[row][col])

    interpolate_this = [
        [80, 80],
        [80, 81],
        [80, 82],
        [80, 83],
        [80, 84],
        [80, 85],
        [80, 86],
        [80, 87],
        [80, 88],
        [80, 89],
        [80, 90],
        [81, 90],
        [82, 90],
        [83, 90],
        [84, 90],
        [85, 90],
        [86, 90],
        [87, 90],
        [88, 90],
        [89, 90],
    ]

    # noinspection PyTypeChecker
    y = interpolate.griddata(points, values, interpolate_this, method='cubic')
    print(y)
    array[10:70, 10:70] = y

    plt.imshow(array)
    plt.show()
    plt.imshow(Z)
    plt.show()
