"""
File with the class NotEnoughPointsError, class to use when there is an error related to the amount of points in
the exporting process
"""

from src.error.shapefile_export_error import ShapefileExportError


class NotEnoughPointsError(ShapefileExportError):
    """
    Class to use when an error related to the amount of points happens when trying to export something to
    shapefile.
    """
    pass
