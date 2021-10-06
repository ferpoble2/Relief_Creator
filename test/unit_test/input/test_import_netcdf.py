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
File with test related to the functionality that imports netcdf files.
"""
import unittest

import numpy as np

from src.error.netcdf_import_error import NetCDFImportError
from src.input.NetCDF import read_info


class TestImportNetcdfFile(unittest.TestCase):

    def test_read_file(self):
        x, y, z = read_info('resources/test_resources/netcdf/test_model.nc')

        self.assertIsInstance(x, np.ndarray)
        self.assertIsInstance(y, np.ndarray)
        self.assertIsInstance(z, np.ndarray)

        np.testing.assert_array_equal(x, np.array([0, 1, 2]), f'{x} is not equal to {[0, 1, 2]}')
        np.testing.assert_array_equal(y, np.array([0, 2, 4]), f'{y} is not equal to {[0, 2, 4]}')
        np.testing.assert_array_equal(z, np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]]),
                                      f'The values of the matrix are not the same as the expected.')

    def test_read_file_real_data_1(self):
        x, y, z = read_info('resources/test_resources/netcdf/test_file_1.nc')
        z = z.reshape(-1)

        self.assertIsInstance(x, np.ndarray)
        self.assertIsInstance(y, np.ndarray)
        self.assertIsInstance(z, np.ndarray)

        x_array = np.load('resources/test_resources/expected_data/npy_data/test_file_1_data_x_array.npy')
        y_array = np.load('resources/test_resources/expected_data/npy_data/test_file_1_data_y_array.npy')

        z_array_part_1 = np.load('resources/test_resources/expected_data/npy_data/test_file_1_data_z_array_part1.npy')
        z_array_part_2 = np.load('resources/test_resources/expected_data/npy_data/test_file_1_data_z_array_part2.npy')

        z_array = np.concatenate((z_array_part_1, z_array_part_2))

        np.testing.assert_array_almost_equal(x, x_array, 3)
        np.testing.assert_array_almost_equal(y, y_array, 3)
        np.testing.assert_array_almost_equal(z, z_array, 3)

    def test_read_file_real_data_2(self):
        x, y, z = read_info('resources/test_resources/netcdf/test_file_2.nc')
        z = z.reshape(-1)

        self.assertIsInstance(x, np.ndarray)
        self.assertIsInstance(y, np.ndarray)
        self.assertIsInstance(z, np.ndarray)

        x_array = np.load('resources/test_resources/expected_data/npy_data/test_file_2_data_x_array.npy')
        y_array = np.load('resources/test_resources/expected_data/npy_data/test_file_2_data_y_array.npy')

        z_array_part_1 = np.load('resources/test_resources/expected_data/npy_data/test_file_2_data_z_array_part1.npy')
        z_array_part_2 = np.load('resources/test_resources/expected_data/npy_data/test_file_2_data_z_array_part2.npy')

        z_array = np.concatenate((z_array_part_1, z_array_part_2))

        np.testing.assert_array_almost_equal(x, x_array, 3)
        np.testing.assert_array_almost_equal(y, y_array, 3)
        np.testing.assert_array_almost_equal(z, z_array, 3)

    def test_read_file_real_data_3(self):
        x, y, z = read_info('resources/test_resources/netcdf/test_file_3.nc')
        z = z.reshape(-1)

        self.assertIsInstance(x, np.ndarray)
        self.assertIsInstance(y, np.ndarray)
        self.assertIsInstance(z, np.ndarray)

        x_array = np.load('resources/test_resources/expected_data/npy_data/test_file_3_data_x_array.npy')
        y_array = np.load('resources/test_resources/expected_data/npy_data/test_file_3_data_y_array.npy')
        z_array = np.load('resources/test_resources/expected_data/npy_data/test_file_3_data_z_array.npy')

        np.testing.assert_array_almost_equal(x, x_array, 3)
        np.testing.assert_array_almost_equal(y, y_array, 3)
        np.testing.assert_array_almost_equal(z, z_array, 3)

    def test_read_info_errors(self):
        # Test files with Y and Z data but not all the X data
        with self.assertRaises(NetCDFImportError):
            read_info('resources/test_resources/netcdf/files_without_data/y_z_data_no_x_range.nc')

        with self.assertRaises(NetCDFImportError):
            read_info('resources/test_resources/netcdf/files_without_data/y_z_data_no_spacing.nc')

        with self.assertRaises(NetCDFImportError):
            read_info('resources/test_resources/netcdf/files_without_data/y_z_data_no_dimension.nc')

        # Test files with X and Z data but not all the Y data
        with self.assertRaises(NetCDFImportError):
            read_info('resources/test_resources/netcdf/files_without_data/x_z_data_no_y_range.nc')

        with self.assertRaises(NetCDFImportError):
            read_info('resources/test_resources/netcdf/files_without_data/x_z_data_no_spacing.nc')

        with self.assertRaises(NetCDFImportError):
            read_info('resources/test_resources/netcdf/files_without_data/x_z_data_no_dimension.nc')

        # Test files with X and Y data but not Z data
        with self.assertRaises(NetCDFImportError):
            read_info('resources/test_resources/netcdf/files_without_data/x_y_data_no_z_data.nc')


if __name__ == '__main__':
    unittest.main()
