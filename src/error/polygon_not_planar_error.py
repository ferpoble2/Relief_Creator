"""
File with the class PolygonNotPlanarError, class to raise when the polygon used is not planar in the model
transformation process.
"""

from src.error.model_transformation_error import ModelTransformationError


class PolygonNotPlanarError(ModelTransformationError):
    """
    Class to raise when the polygon is not planar in the model transformation process
    """
    pass
