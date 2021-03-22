"""
File with the class ModelTransformationError, class to raise when there is an error in the transformation process.
"""

from src.error.scene_error import SceneError


class ModelTransformationError(SceneError):
    """
    Class to use when there is an error in the transformation process of a model.
    """
    pass
