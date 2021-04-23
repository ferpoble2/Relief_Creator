"""
File that contains all the exceptions related to the scene.
"""

from src.error.base_error import BaseError


class SceneError(BaseError):
    """
    Class used to represent the scene related exceptions.
    """

    def __init__(self, code: int = 0):
        """
        Constructor of the class

        Args:
            code: Code of the error.
        """
        super(SceneError, self).__init__(code)

        self.codes = {
            0: 'Default Error',
            1: 'Polygon used is not planar.',
            2: 'The polygon used doesnt have at least 3 vertices.',
            3: 'Can not use that model for transforming points. Try using a Map2DModel.',
            4: 'Polygon id can not be None.'
        }
