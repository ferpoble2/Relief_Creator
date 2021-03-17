"""
File that contains the WrongInterpolationTypeError class, class to use when there is problems
with the type of export to use.
"""

from src.error.GUI_error import GUIError


class WrongInterpolationTypeError(GUIError):
    """
    Class to use when there is problems with the type of the interpolation.
    """
    pass
