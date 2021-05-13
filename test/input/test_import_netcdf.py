"""
File with test related to the functionality that imports netcdf files.
"""

import unittest
import numpy as np
import json

from src.input.NetCDF import read_info

FILES_DIRECTORY = './test/input/files/'


class TestImportNetcdfFile(unittest.TestCase):

    def test_read_file(self):
        x, y, z = read_info(FILES_DIRECTORY + 'test_model.nc')

        self.assertIsInstance(x, np.ndarray)
        self.assertIsInstance(y, np.ndarray)
        self.assertIsInstance(z, np.ndarray)

        self.assertTrue((x == np.array([0, 1, 2])).all())
        self.assertTrue((y == np.array([0, 2, 4])).all(), f'{y} is not equal to {[0, 2, 4]}')
        self.assertTrue((z == np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])).all())

    def test_read_file_real_data_1(self):
        x, y, z = read_info(FILES_DIRECTORY + 'test_file_1.nc')
        z = z.reshape(-1)

        self.assertIsInstance(x, np.ndarray)
        self.assertIsInstance(y, np.ndarray)
        self.assertIsInstance(z, np.ndarray)

        with open(FILES_DIRECTORY + 'test_file_1_data.json') as f:
            data_file_1 = json.load(f)

            self.assertTrue((x == data_file_1['x']).all())
            self.assertTrue((y == data_file_1['y']).all())
            self.assertTrue((z == data_file_1['z']).all())

    def test_read_file_real_data_2(self):
        x, y, z = read_info(FILES_DIRECTORY + 'test_file_2.nc')
        z = z.reshape(-1)

        self.assertIsInstance(x, np.ndarray)
        self.assertIsInstance(y, np.ndarray)
        self.assertIsInstance(z, np.ndarray)

        with open(FILES_DIRECTORY + 'test_file_2_data.json') as f:
            data_file_1 = json.load(f)

            self.assertTrue((x == data_file_1['x']).all())
            self.assertTrue((y == data_file_1['y']).all())
            self.assertTrue((z == data_file_1['z']).all())

    def test_read_file_real_data_3(self):
        x, y, z = read_info(FILES_DIRECTORY + 'test_file_3.nc')
        z = z.reshape(-1)

        self.assertIsInstance(x, np.ndarray)
        self.assertIsInstance(y, np.ndarray)
        self.assertIsInstance(z, np.ndarray)

        with open(FILES_DIRECTORY + 'test_file_3_data.json') as f:
            data_file_1 = json.load(f)

            self.assertTrue((x == data_file_1['x']).all())
            self.assertTrue((y == data_file_1['y']).all())
            self.assertTrue((z == data_file_1['z']).all())


if __name__ == '__main__':
    unittest.main()
