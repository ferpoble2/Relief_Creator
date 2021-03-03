"""
File that contains all the exceptions related to the polygons.
"""


class PolygonError(Exception):
    """
    Class used to represent the polygon related exceptions.
    """
    pass


class RepeatedPointError(PolygonError):
    """
    Class that represents when an error related to repeated points happens.
    """
    pass


class LineIntersectionError(PolygonError):
    """
    Class that represent when an error related to the intersection of lines happens.
    """
    pass
