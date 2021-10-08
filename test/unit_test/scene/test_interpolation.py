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
File with the tests related to the interpolation functionality.
"""

import os
import unittest
import warnings

import numpy as np

from src.engine.scene.interpolation.cubic_interpolation import CubicInterpolation
from src.engine.scene.interpolation.linear_interpolation import LinearInterpolation
from src.engine.scene.interpolation.nearest_interpolation import NearestInterpolation
from src.engine.scene.interpolation.smooth_interpolation import SmoothInterpolation
from src.engine.scene.transformation.linear_transformation import LinearTransformation
from src.input.NetCDF import read_info
from test.test_case import ProgramTestCase


class TestSmoothingInterpolation(ProgramTestCase):

    def setUp(self) -> None:
        """
        Logic that runs at the beginning o every tests.

        Returns: None
        """
        super().setUp()
        warnings.simplefilter('ignore', category=DeprecationWarning)

        # initialize variables
        self.engine.create_model_from_file('resources/test_resources/cpt/cpt_1.cpt',
                                           'resources/test_resources/netcdf/test_file_1.nc')

    def test_smoothing_normal_application(self):
        # load list of polygons
        self.engine.create_polygon_from_file('resources/test_resources/polygons/shape_one_polygon_2.shp')

        # apply transformation with filters
        interpolation = SmoothInterpolation(self.engine.get_active_model_id(),
                                            self.engine.get_active_polygon_id(),
                                            2)
        self.engine.interpolate_points(interpolation)

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
        self.engine.create_polygon_from_file('resources/test_resources/polygons/shape_one_polygon_2.shp')

        # apply transformation with filters
        for _ in range(5):
            interpolation = SmoothInterpolation(self.engine.get_active_model_id(),
                                                self.engine.get_active_polygon_id(),
                                                2)
            self.engine.interpolate_points(interpolation)

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


class TestCubicInterpolation(ProgramTestCase):

    def setUp(self) -> None:
        """
        Logic that runs at the beginning o every tests.

        Returns: None
        """
        super().setUp()
        warnings.simplefilter('ignore', category=DeprecationWarning)
        self.engine.create_model_from_file('resources/test_resources/cpt/cpt_1.cpt',
                                           'resources/test_resources/netcdf/test_file_1.nc')

    def test_cubic_normal_application(self):
        # load list of polygons
        self.engine.create_polygon_from_file('resources/test_resources/polygons/shape_one_polygon_2.shp')

        # apply transformation with filters
        transformation = LinearTransformation(self.engine.get_active_model_id(),
                                              self.engine.get_active_polygon_id(),
                                              2000,
                                              3000)
        self.engine.transform_points(transformation)

        # apply interpolation
        interpolation = CubicInterpolation(self.engine.get_active_model_id(),
                                           self.engine.get_active_polygon_id(),
                                           2)
        self.engine.interpolate_points(interpolation)

        # export model to compare data
        self.engine.export_model_as_netcdf(self.engine.get_active_model_id(),
                                           'resources/test_resources/temp/temp_interpolation_2')

        # read data and compare
        info_written = read_info('resources/test_resources/temp/temp_interpolation_2.nc')
        info_expected = read_info('resources/test_resources/expected_data/netcdf/expected_interpolation_2.nc')

        self.assertTrue((info_written[0] == info_expected[0]).all(),
                        'Info on the x array is not equal to the expected.')
        self.assertTrue((info_written[1] == info_expected[1]).all(),
                        'Info on the y array is not equal to the expected.')
        self.assertTrue((info_written[2] == info_expected[2]).all(),
                        'Info on the height matrix is not equal to the expected.')

        os.remove('resources/test_resources/temp/temp_interpolation_2.nc')


class TestNearestInterpolation(ProgramTestCase):

    def setUp(self) -> None:
        """
        Logic that runs at the beginning o every tests.

        Returns: None
        """
        super().setUp()
        warnings.simplefilter('ignore', category=DeprecationWarning)
        self.engine.create_model_from_file('resources/test_resources/cpt/cpt_1.cpt',
                                           'resources/test_resources/netcdf/test_file_1.nc')

    def test_nearest_normal_application(self):
        # load list of polygons
        self.engine.create_polygon_from_file('resources/test_resources/polygons/shape_one_polygon_2.shp')

        # apply transformation with filters
        transformation = LinearTransformation(self.engine.get_active_model_id(),
                                              self.engine.get_active_polygon_id(),
                                              2000,
                                              3000)
        self.engine.transform_points(transformation)

        # apply interpolation
        interpolation = NearestInterpolation(self.engine.get_active_model_id(),
                                             self.engine.get_active_polygon_id(),
                                             2)
        self.engine.interpolate_points(interpolation)

        # export model to compare data
        self.engine.export_model_as_netcdf(self.engine.get_active_model_id(),
                                           'resources/test_resources/temp/temp_interpolation_3')

        # read data and compare
        info_written = read_info('resources/test_resources/temp/temp_interpolation_3.nc')
        info_expected = read_info('resources/test_resources/expected_data/netcdf/expected_interpolation_3.nc')

        self.assertTrue((info_written[0] == info_expected[0]).all(),
                        'Info on the x array is not equal to the expected.')
        self.assertTrue((info_written[1] == info_expected[1]).all(),
                        'Info on the y array is not equal to the expected.')
        self.assertTrue((info_written[2] == info_expected[2]).all(),
                        'Info on the height matrix is not equal to the expected.')

        os.remove('resources/test_resources/temp/temp_interpolation_3.nc')


class TestLinearInterpolation(ProgramTestCase):

    def setUp(self) -> None:
        """
        Logic that runs at the beginning o every tests.

        Returns: None
        """
        super().setUp()
        warnings.simplefilter('ignore', category=DeprecationWarning)
        self.engine.create_model_from_file('resources/test_resources/cpt/cpt_1.cpt',
                                           'resources/test_resources/netcdf/test_file_1.nc')

    def test_linear_normal_application(self):
        # load list of polygons
        self.engine.create_polygon_from_file('resources/test_resources/polygons/shape_one_polygon_2.shp')

        # apply transformation with filters
        transformation = LinearTransformation(self.engine.get_active_model_id(),
                                              self.engine.get_active_polygon_id(),
                                              2000,
                                              3000)
        self.engine.transform_points(transformation)

        # apply interpolation
        interpolation = LinearInterpolation(self.engine.get_active_model_id(),
                                            self.engine.get_active_polygon_id(),
                                            2)
        self.engine.interpolate_points(interpolation)

        # export model to compare data
        self.engine.export_model_as_netcdf(self.engine.get_active_model_id(),
                                           'resources/test_resources/temp/temp_interpolation_1')

        # read data and compare
        info_written = read_info('resources/test_resources/temp/temp_interpolation_1.nc')
        info_expected = read_info('resources/test_resources/expected_data/netcdf/expected_interpolation_1.nc')

        self.assertTrue((info_written[0] == info_expected[0]).all(),
                        'Info on the x array is not equal to the expected.')
        self.assertTrue((info_written[1] == info_expected[1]).all(),
                        'Info on the y array is not equal to the expected.')
        self.assertTrue((info_written[2] == info_expected[2]).all(),
                        'Info on the height matrix is not equal to the expected.')

        os.remove('resources/test_resources/temp/temp_interpolation_1.nc')


if __name__ == '__main__':
    unittest.main()
