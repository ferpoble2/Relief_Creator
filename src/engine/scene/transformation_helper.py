"""
File with the class TransformationHelper, class in charge of making transformation to the points of different models.
"""
import numpy as np


class TransformationHelper:
    """
    Class in charge of executing transformation to different models in the scene.
    """

    def __init__(self):
        """
        Constructor of the class.
        """
        pass

    def modify_points_inside_polygon(self, points: np.ndarray, polygon: 'Polygon', new_height):
