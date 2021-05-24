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
import unittest
import numpy as np
import os

from src.output.netcdf_exporter import NetcdfExporter
from src.input.NetCDF import read_info


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


if __name__ == '__main__':
    unittest.main()
