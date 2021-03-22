"""
File with the class PolygonPointError, class to raise when there is a problem with the points in the polygon
in the transformation process.
"""

from src.error.model_transformation_error import ModelTransformationError


class PolygonPointNumberError(ModelTransformationError):
    """
    Class to raise when there is a problem with the points of the polygon in the model transformation process.
    """
    pass