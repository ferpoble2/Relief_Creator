"""
File with the InterpolationError class, class to use when raising exceptions related to the interpolation process.
"""

from src.error.scene_error import SceneError


class InterpolationError(SceneError):
    """
    Class to use when there is an error in the transformation process of a model.
    """

    def __init__(self, code: int = 0):
        """
        Constructor of the class.
        """
        self.code = code

        self.codes = {
            0: 'Error description not selected.',
            1: 'Not enough points in the polygon to do the interpolation.',
            2: 'Distance must be greater than 0 to realize the interpolation.',
            3: 'Can not interpolate model that is not an instance of Map2DModel.'
        }
