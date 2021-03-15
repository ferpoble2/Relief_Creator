"""
File with the class UnknownDataType, class to use when there is an error related to an unknown data type in the
exporting process.
"""

from src.error.shapefile_export_error import ShapefileExportError


class UnknownDataTypeError(ShapefileExportError):
    """
    Class to use when an error related to unknowns data types
    """
    pass
