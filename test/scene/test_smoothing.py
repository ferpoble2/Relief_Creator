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
File with the tests related to the smoothing functionality.
"""
import os
import unittest
import warnings

import numpy as np

from src.input.NetCDF import read_info
from src.program.program import Program


class TestSmoothing(unittest.TestCase):

    def setUp(self) -> None:
        """
        Logic that runs at the beginning o every tests.

        Returns: None
        """
        warnings.simplefilter("ignore", ResourceWarning)
        warnings.simplefilter('ignore', category=DeprecationWarning)

        # create program
        self.program = Program()
        self.engine = self.program.engine

        # initialize variables
        self.engine.should_use_threads(False)
        self.engine.load_netcdf_file('resources/test_resources/cpt/cpt_1.cpt',
                                     'resources/test_resources/netcdf/test_file_1.nc')

    def tearDown(self) -> None:
        """
        Delete all temporary files created by the program on the setup or testing processes.

        Returns: None
        """
        self.program.close()

    def test_smoothing_normal_application(self):
        # load list of polygons
        self.engine.load_shapefile_file('resources/test_resources/polygons/shape_one_polygon_2.shp')

        # apply transformation with filters
        self.engine.scene.apply_smoothing_algorithm(self.engine.get_active_polygon_id(),
                                                    self.engine.get_active_model_id(),
                                                    2)

        # export model to compare data
        self.engine.export_model_as_netcdf(self.engine.get_active_model_id(),
                                           'resources/test_resources/temp/temp_smoothing_1')

        # read data and compare
        info_written = read_info('resources/test_resources/temp/temp_smoothing_1.nc')
        info_expected = read_info('resources/test_resources/expected_data/netcdf/expected_smoothing_1.nc')

        np.testing.assert_array_equal(info_written[0],
                                      info_expected[0],
                                      'Info on the x array is not equal to the expected.')
        np.testing.assert_array_equal(info_written[1],
                                      info_expected[1],
                                      'Info on the y array is not equal to the expected.')
        np.testing.assert_array_almost_equal(info_written[2],
                                             info_expected[2],
                                             3,
                                             'Info on the height matrix is not equal to the expected.')

        os.remove('resources/test_resources/temp/temp_smoothing_1.nc')

    def test_smoothing_multiple_applications(self):
        # load list of polygons
        self.engine.load_shapefile_file('resources/test_resources/polygons/shape_one_polygon_2.shp')

        # apply transformation with filters
        for _ in range(5):
            self.engine.scene.apply_smoothing_algorithm(self.engine.get_active_polygon_id(),
                                                        self.engine.get_active_model_id(),
                                                        2)

        # export model to compare data
        self.engine.export_model_as_netcdf(self.engine.get_active_model_id(),
                                           'resources/test_resources/temp/temp_smoothing_2')

        # read data and compare
        info_written = read_info('resources/test_resources/temp/temp_smoothing_2.nc')
        info_expected = read_info('resources/test_resources/expected_data/netcdf/expected_smoothing_2.nc')

        np.testing.assert_array_equal(info_written[0],
                                      info_expected[0],
                                      'Info on the x array is not equal to the expected.')
        np.testing.assert_array_equal(info_written[1],
                                      info_expected[1],
                                      'Info on the y array is not equal to the expected.')
        np.testing.assert_array_almost_equal(info_written[2],
                                             info_expected[2],
                                             3,
                                             'Info on the height matrix is not equal to the expected.')

        os.remove('resources/test_resources/temp/temp_smoothing_2.nc')


if __name__ == '__main__':
    unittest.main()
