"""
File with the class NetcdfExporter, class in charge of exporting information of the models to a netcdf file.
"""

from netCDF4 import Dataset
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
        root_grp = Dataset(f'{filename}.netcdf', "w", format="NETCDF4")
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
