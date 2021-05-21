"""
File with test related to the functionality that imports netcdf files.
"""

import unittest
import numpy as np
import os

from src.input.NetCDF import read_info


class TestImportNetcdfFile(unittest.TestCase):

    def test_read_file(self):
        x, y, z = read_info('resources/test_resources/netcdf/test_model.nc')

        self.assertIsInstance(x, np.ndarray)
        self.assertIsInstance(y, np.ndarray)
        self.assertIsInstance(z, np.ndarray)

        self.assertTrue((x == np.array([0, 1, 2])).all())
        self.assertTrue((y == np.array([0, 2, 4])).all(), f'{y} is not equal to {[0, 2, 4]}')
        self.assertTrue((z == np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])).all())

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

        self.assertTrue((x == x_array).all())
        self.assertTrue((y == y_array).all())
        self.assertTrue((z == z_array).all())

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

        self.assertTrue((x == x_array).all())
        self.assertTrue((y == y_array).all())
        self.assertTrue((z == z_array).all())

    def test_read_file_real_data_3(self):
        x, y, z = read_info('resources/test_resources/netcdf/test_file_3.nc')
        z = z.reshape(-1)

        self.assertIsInstance(x, np.ndarray)
        self.assertIsInstance(y, np.ndarray)
        self.assertIsInstance(z, np.ndarray)

        x_array = np.load('resources/test_resources/expected_data/npy_data/test_file_3_data_x_array.npy')
        y_array = np.load('resources/test_resources/expected_data/npy_data/test_file_3_data_y_array.npy')
        z_array = np.load('resources/test_resources/expected_data/npy_data/test_file_3_data_z_array.npy')

        self.assertTrue((x == x_array).all())
        self.assertTrue((y == y_array).all())
        self.assertTrue((z == z_array).all())


if __name__ == '__main__':
    unittest.main()
