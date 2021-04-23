"""
File that contains the NonExistingPolygonError
"""
from src.error.scene_error import SceneError


class NonExistentPolygonError(SceneError):
    """
    Class used to represent when an polygon doesnt exist in the scene
    """

    def __init__(self, code: int = 0):
        """
        Constructor of the class
        """
        super(NonExistentPolygonError, self).__init__(code)

        self.codes = {
            0: 'Default Error',
        }
