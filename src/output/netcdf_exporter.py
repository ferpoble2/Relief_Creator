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
File with the class NetcdfExporter, class in charge of exporting information of the models to a netcdf file.
"""

from netCDF4 import Dataset
from src.utils import HEIGHT_KEYS
from src.error.export_error import ExportError

import numpy as np


class NetcdfExporter:
    """
    Class in charge of the export of the information of models.
    """

    def __init__(self):
        """
        Constructor of the class
        """
        pass

    def modify_heights_existent_netcdf_file(self,
                                            heights: np.ndarray,
                                            filename='./temp_model_file.nc'):
        """
        Modify the height array stored in an existent netcdf file.

        The value stored in the variable who stores the information of the height of the map is changed using the
        specified heights.

        Args:
            heights: New heights to store in the netcdf file.
            filename: Directory + filename to modify. Default value is the one created for the read_info method
                      from the Input module.

        Returns: None
        """
        root_grp = Dataset(filename, 'r+')
        grp_keys = root_grp.variables.keys()

        # Check for the key to be in the object
        height_key = None
        for key in HEIGHT_KEYS:
            if key in grp_keys:
                height_key = key
                break

        if height_key is None:
            raise ExportError(3)

        height_shape = root_grp.variables[height_key].shape
        root_grp.variables[height_key][:] = heights.reshape(height_shape)
        root_grp.variables[height_key].actual_range = np.array([np.nanmin(heights), np.nanmax(heights)])
        root_grp.close()

    def export_model_vertices_to_netcdf_file(self,
                                             vertices: np.ndarray,
                                             filename='Model') -> None:
        """
        Export the information of the vertices of a model to a netcdf file.

        Args:
            vertices: Information of the vertices. (shape must be (x, y, 3))
            filename: Name of the file to use.

        Returns: None
        """
        root_grp = Dataset(f'{filename}.nc', "w", format="NETCDF4")
        root_grp.createDimension('lon', len(vertices[0]))
        root_grp.createDimension('lat', len(vertices))

        lat = root_grp.createVariable('lat', np.float32, ('lat',))
        lat.units = 'degrees_north'
        lat.long_name = 'latitude'

        lon = root_grp.createVariable('lon', np.float32, ('lon',))
        lon.units = 'degrees_east'
        lon.long_name = 'longitude'

        z = root_grp.createVariable('z', np.float32, ('lat', 'lon'))
        z.long_name = 'z'

        x_values = vertices[0, :, 0].reshape(-1)
        y_values = vertices[:, 0, 1].reshape(-1)  # flip the array since netcdf uses cartesian coordinates
        z_values = vertices[:, :, 2].reshape((vertices.shape[0], vertices.shape[1]))

        lon[:] = x_values
        lat[:] = y_values
        z[:] = z_values

        root_grp.close()
