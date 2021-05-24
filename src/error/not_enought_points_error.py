# BEGIN GPL LICENSE BLOCK
#
#     This program is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# END GPL LICENSE BLOCK

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
