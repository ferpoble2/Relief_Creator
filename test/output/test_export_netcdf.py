#  BEGIN GPL LICENSE BLOCK
#
#      This program is free software: you can redistribute it and/or modify
#      it under the terms of the GNU General Public License as published by
#      the Free Software Foundation, either version 3 of the License, or
#      (at your option) any later version.
#
#      This program is distributed in the hope that it will be useful,
#      but WITHOUT ANY WARRANTY; without even the implied warranty of
#      MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#      GNU General Public License for more details.
#
#      You should have received a copy of the GNU General Public License
#      along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
#  END GPL LICENSE BLOCK

"""
File with test related to the functionality of exporting netcdf files.
"""
import os
import shutil
import unittest

import numpy as np

from src.error.export_error import ExportError
from src.input.NetCDF import read_info
from src.output.netcdf_exporter import NetcdfExporter


class TestExportNetcdfFile(unittest.TestCase):

    def test_file_consistency(self):
        exporter = NetcdfExporter()
        exporter.export_model_vertices_to_netcdf_file(np.array([(0, 0, 1), (1, 0, 2), (2, 0, 3),
                                                                (0, 2, 4), (1, 2, 5), (2, 2, 6),
                                                                (0, 4, 7), (1, 4, 8), (2, 4, 9)]).reshape(3, 3, 3),
                                                      'resources/test_resources/temp/test_model_temp')

        x, y, z = read_info('resources/test_resources/temp/test_model_temp.nc')
        generated_x = np.array([0, 1, 2])
        generated_y = np.array([0, 2, 4])
        generated_z = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])

        self.assertTrue((generated_x == x).all(), f'Data loaded is not equal to data expected. {generated_x} != {x}')
        self.assertTrue((generated_y == y).all(), f'Data loaded is not equal to data expected. {generated_y} != {y}')
        self.assertTrue((generated_z == z).all(), f'Data loaded is not equal to data expected. {generated_z} != {z}')

        os.remove('resources/test_resources/temp/test_model_temp.nc')

    def test_export_file_no_keys(self):
        exporter = NetcdfExporter()

        # Should not modify the file in any way
        with self.assertRaises(ExportError):
            exporter.modify_heights_existent_netcdf_file(np.array([]),
                                                         'resources/test_resources/netcdf/files_without_data/'
                                                         'file_no_keys.nc')

    def test_export_one_dimension_heights(self):
        exporter = NetcdfExporter()

        # Copy file to modify to not modify the original file
        shutil.copy('resources/test_resources/netcdf/test_file_4.nc',
                    'resources/test_resources/temp/one_dimension_file.nc')

        # Read the info of the file and generate new data with the same dimension that the one stored in the file
        x, y, z = read_info('resources/test_resources/temp/one_dimension_file.nc')
        new_data = np.zeros(z.shape)

        # Modify the data of the file and read it to compare
        exporter.modify_heights_existent_netcdf_file(new_data,
                                                     'resources/test_resources/temp/one_dimension_file.nc')
        new_x, new_y, new_z = read_info('resources/test_resources/temp/one_dimension_file.nc')

        # Compare the data of the file
        self.assertTrue((new_x == x).all())
        self.assertTrue((new_y == y).all())
        self.assertTrue((new_z == new_data).all())

        # Delete temporal files generated in the test
        os.remove('resources/test_resources/temp/one_dimension_file.nc')

    def test_export_file_actual_range_metadata(self):
        """
        Test the export of a file with the metadata actual_range inside the variable that stores the heights of the
        maps.
        """
        exporter = NetcdfExporter()

        # Copy file to modify to not modify the original file
        shutil.copy('resources/test_resources/netcdf/test_file_1.nc',
                    'resources/test_resources/temp/actual_range_metadata_file.nc')

        # Read the info of the file and generate new data with the same dimension that the one stored in the file
        x, y, z = read_info('resources/test_resources/temp/actual_range_metadata_file.nc')
        new_data = np.zeros(z.shape)

        # Modify the data of the file and read it to compare
        exporter.modify_heights_existent_netcdf_file(new_data,
                                                     'resources/test_resources/temp/actual_range_metadata_file.nc')
        new_x, new_y, new_z = read_info('resources/test_resources/temp/actual_range_metadata_file.nc')

        # Compare the data of the file
        self.assertTrue((new_x == x).all())
        self.assertTrue((new_y == y).all())
        self.assertTrue((new_z == new_data).all())

        # Delete temporal files generated in the test
        os.remove('resources/test_resources/temp/actual_range_metadata_file.nc')


if __name__ == '__main__':
    unittest.main()
