"""
File with the class TransformationHelper, class in charge of making transformation to the points of different models.
"""
import numpy as np
from typing import List

from matplotlib import path
from src.utils import interpolate


class TransformationHelper:
    """
    Class in charge of executing transformation to different models in the scene.
    """

    def __init__(self):
        """
        Constructor of the class.
        """
        pass

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

        Returns: numpy.ndarray with the new points
        """
        flags = self.__generate_mask(points, polygon_points)

        # modify the height linearly
        current_min_height = np.min(height[flags])
        current_max_height = np.max(height[flags])

        new_height = interpolate(height[flags], current_min_height, current_max_height, new_min_height, new_max_height,
                                 False)

        height[flags] = new_height
        return height

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
        flags = p.contains_points(np.hstack((xv.flatten()[:, np.newaxis], yv.flatten()[:, np.newaxis])))
        flags = flags.reshape(xv.shape)
        return flags
