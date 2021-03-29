"""
File with the class TransformationHelper, class in charge of making transformation to the points of different models.
"""
import numpy as np
from shapely.geometry.polygon import LinearRing as LinearRing
from typing import List
from matplotlib import path
from scipy import interpolate as interpolate_2d_array

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

    def __generate_mask(self, points, polygon_points) -> np.ndarray:
        """
        Generate a mask of the points that are inside the specified polygon.

        Mask is a numpy array with booleans representing if the point is inside the polygon or not.

        Args:
            points: Numpy array with the points (shape must be (x, y, 3))
            polygon_points: List with the points of the polygon. [x1, y1, z1, x2, y2, z2, ...]

        Returns: Numpy array with booleans indicating if the points are inside the polygon or not.
        """

        # generate the polygon
        points_2d = []
        for point_ind in range(len(polygon_points)):
            if point_ind % 3 == 0:
                points_2d.append((polygon_points[point_ind], polygon_points[point_ind + 1]))
        # get a mask for the points inside
        xv = points[:, :, 0]
        yv = points[:, :, 1]
        p = path.Path(points_2d)

        # noinspection PyTypeChecker
        flags = p.contains_points(np.hstack((xv.flatten()[:, np.newaxis], yv.flatten()[:, np.newaxis])))
        flags = flags.reshape(xv.shape)
        return flags

    # noinspection PyShadowingNames
    def __interpolate_nan(self, array_2d: np.ndarray, interpolation_type: str = 'linear') -> np.ndarray:
        """
        Interpolate the missing values from the array2d using scipy interpolation method.

        Args:
            array_2d: Array 2D with missing values to interpolate.
            interpolation_type: Type of the interpolation. (nearest, linear, cubic)

        Returns: Array interpolated.
        """
        raise NotImplementedError()

    def modify_points_inside_polygon_linear(self, points: np.ndarray,
                                            height: np.ndarray,
                                            polygon_points: List[float],
                                            new_max_height: float,
                                            new_min_height: float) -> np.ndarray:
        """
        Modify the points that are inside the polygon changing their height using a linear interpolation
        given the new specified height.

        Args:
            height: Array with the height of the points. must have shape (x, y)
            points: Points to modify (numpy array of points), must have shape (x, y, 3)
            polygon_points: List of points in the polygon. [x1, y1, z1, x2, y2, z2, ...]
            new_max_height: New height to interpolate the points
            new_min_height: New height to interpolate the points

        Returns: numpy.array with the new points
        """
        flags = self.__generate_mask(points, polygon_points)

        # modify the height linearly
        current_min_height = np.min(height[flags])
        current_max_height = np.max(height[flags])

        new_height = interpolate(height[flags], current_min_height, current_max_height, new_min_height, new_max_height,
                                 False)

        height[flags] = new_height
        return height

    def interpolate_points_external_to_polygon(self, points: np.ndarray, polygon_points: list,
                                               heights: np.ndarray, distance: float) -> np.ndarray:
        """
        Interpolate the points that are external to the polygon until a certain distance.

        Args:
            distance: Limit distance to interpolate the points from.
            points: Points of the model. (shape must be (x, y, 3))
            polygon_points: List with the points of the polygon. [x1, y1, z1, x2, y2, z2, ...]
            heights: Array with the height of the points. must have shape (x, y)

        Returns: Array of heights with height of the points external to the polygon modified.
        """
        log.debug('Interpolate points external to polygon')

        points_no_z_axis = self.__delete_z_axis(polygon_points)

        # check if the points are already CW
        if is_clockwise(points_no_z_axis):  # points must be in CCW direction
            points_no_z_axis.reverse()

        # create a polygon external to the one proportionated
        closed_polygon = LinearRing(points_no_z_axis)
        exterior_polygon = closed_polygon.buffer(distance).exterior

        x_coords, y_coords = exterior_polygon.xy
        polygon_exterior = []

        for x_coordinate, y_coordinate in zip(x_coords, y_coords):
            polygon_exterior.append(x_coordinate)
            polygon_exterior.append(y_coordinate)
            polygon_exterior.append(0.5)

        # generate a mask of the internal points
        log.debug('Generating masks')
        mask_external = self.__generate_mask(points, polygon_exterior)
        mask_internal = self.__generate_mask(points, polygon_points)

        # apply the logical operations
        in_between_mask = mask_external != mask_internal
        heights[in_between_mask == True] = np.nan

        # apply the interpolation algorithm from scipy
        log.debug('Interpolating using numpy')
        heights = self.__interpolate_nan(heights)

        log.debug('Ploting')
        import matplotlib.pyplot as plt
        plt.imshow(heights)
        plt.show()

        return heights

    def get_max_min_inside_polygon(self, points: np.ndarray, polygon_points: List[float], heights: np.ndarray) -> tuple:
        """
        Extract the maximum and minimum value of the points that are inside the polygon.

        Args:
            points: Points of the model. (shape must be (x, y, 3))
            polygon_points: List with the points of the polygon. [x1, y1, z1, x2, y2, z2, ...]
            heights: height: Array with the height of the points. must have shape (x, y)

        Returns: Tuple with the maximum and minimum value
        """
        flags = self.__generate_mask(points, polygon_points)

        maximum = np.max(heights[flags])
        minimum = np.min(heights[flags])

        return maximum, minimum


if __name__ == '__main__':
    # points_2d = [[0, 0], [0, 1], [0, 2], [1, 1], [1, 0]]
    #
    # # check if the points are already CW
    # if is_clockwise(points_2d):  # points must be in CCW direction
    #     points_2d.reverse()
    #
    # linear_ring = LinearRing(points_2d)
    #
    # points_2d.append(points_2d[0])  # make it closed
    # linear_ring2 = linear_ring.buffer(8)
    #
    # import matplotlib.pyplot as plt
    #
    # exterior = linear_ring2.exterior
    #
    # x, y = linear_ring.xy
    # x2, y2 = exterior.xy
    #
    # plt.plot(x, y, color='red')
    # plt.plot(x2, y2, color='green')
    # plt.show()

    import numpy as np
    from scipy import interpolate
    import matplotlib.pyplot as plt

    # Let's create some random  data
    array = np.random.random_integers(0, 10, (10, 10)).astype(float)
    # values grater then 7 goes to np.nan
    array[2:10, 2:10] = np.nan

    x = np.arange(0, array.shape[1])
    y = np.arange(0, array.shape[0])
    # mask invalid values
    array = np.ma.masked_invalid(array)
    xx, yy = np.meshgrid(x, y)
    # get only the valid values
    x1 = xx[~array.mask]
    y1 = yy[~array.mask]
    newarr = array[~array.mask]

    GD1 = interpolate.griddata((x1, y1), newarr.ravel(),
                               (xx, yy),
                               method='linear')

    plt.imshow(array)
    plt.show()
    plt.imshow(GD1)
    plt.show()
