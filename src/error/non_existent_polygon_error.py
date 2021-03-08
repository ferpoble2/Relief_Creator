"""
File that contains the NonExistingPolygonError
"""
from src.error.scene_error import SceneError


class NonExistentPolygonError(SceneError):
    """
    Class used to represent when an polygon doesnt exist in the scene
    """
    pass
