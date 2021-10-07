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
File with the tests related to the modifications of the height to the points inside the polygons.
"""
import os
import warnings

import numpy as np

from src.engine.scene.transformation.fill_nan_transformation import FillNanTransformation
from src.engine.scene.transformation.linear_transformation import LinearTransformation
from src.input.NetCDF import read_info
from test.test_case import ProgramTestCase


class TestModifyHeightLinear(ProgramTestCase):

    def setUp(self) -> None:
        """
        Code executed before every test on the testcase.
        """
        super().setUp()
        warnings.simplefilter('ignore', DeprecationWarning)

    def test_linear_transformation(self):
        self.engine.create_model_from_file('resources/test_resources/cpt/cpt_1.cpt',
                                           'resources/test_resources/netcdf/test_file_1.nc')

        # load list of polygons
        self.engine.create_polygon_from_file('resources/test_resources/polygons/shape_one_polygon_south_america.shp')

        # apply transformation with filters
        transformation = LinearTransformation(self.engine.get_active_model_id(),
                                              self.engine.get_active_polygon_id(),
                                              2000,
                                              3000)
        self.engine.transform_points(transformation)

        # export model to compare data
        self.engine.export_model_as_netcdf(self.engine.get_active_model_id(),
                                           'resources/test_resources/temp/temp_transformation_1')

        # read data and compare
        info_written = read_info('resources/test_resources/temp/temp_transformation_1.nc')
        info_expected = read_info('resources/test_resources/expected_data/netcdf/expected_transformation_1.nc')

        np.testing.assert_array_almost_equal(info_written[0], info_expected[0], 3,
                                             'Info on the x array is not equal to the expected.')
        np.testing.assert_array_almost_equal(info_written[1], info_expected[1], 3,
                                             'Info on the y array is not equal to the expected.')
        np.testing.assert_array_almost_equal(info_written[2], info_expected[2], 3,
                                             'Info on the height matrix is not equal to the expected.')

        os.remove('resources/test_resources/temp/temp_transformation_1.nc')


class TestFillNanTransformation(ProgramTestCase):

    def setUp(self) -> None:
        """
        Code executed before every test on the testcase.
        """
        super().setUp()
        warnings.simplefilter('ignore', DeprecationWarning)

    def test_fill_nan_transformation(self):
        self.engine.create_model_from_file('resources/test_resources/cpt/cpt_1.cpt',
                                           'resources/test_resources/netcdf/test_file_1.nc')

        # load list of polygons
        self.engine.create_polygon_from_file('resources/test_resources/polygons/shape_one_polygon_south_america.shp')

        # apply transformation with filters
        transformation = FillNanTransformation(self.engine.get_active_model_id(),
                                               self.engine.get_active_polygon_id())
        self.engine.transform_points(transformation)

        # export model to compare data
        self.engine.export_model_as_netcdf(self.engine.get_active_model_id(),
                                           'resources/test_resources/temp/temp_transformation_2')

        # read data and compare
        info_written = read_info('resources/test_resources/temp/temp_transformation_2.nc')
        info_expected = read_info('resources/test_resources/expected_data/netcdf/expected_transformation_3.nc')

        np.testing.assert_array_almost_equal(info_written[0], info_expected[0], 3,
                                             'Info on the x array is not equal to the expected.')
        np.testing.assert_array_almost_equal(info_written[1], info_expected[1], 3,
                                             'Info on the y array is not equal to the expected.')
        np.testing.assert_array_almost_equal(info_written[2], info_expected[2], 3,
                                             'Info on the height matrix is not equal to the expected.')

        os.remove('resources/test_resources/temp/temp_transformation_2.nc')

    def test_fill_nan_transformation_polygon_outside_map(self):
        self.engine.create_model_from_file('resources/test_resources/cpt/cpt_1.cpt',
                                           'resources/test_resources/netcdf/test_file_1.nc')

        # load list of polygons
        polygon_id = self.engine.create_new_polygon()
        self.engine.set_active_polygon(polygon_id)
        self.engine.add_new_vertex_to_active_polygon_using_real_coords(-5000, -5000)
        self.engine.add_new_vertex_to_active_polygon_using_real_coords(-4000, -5000)
        self.engine.add_new_vertex_to_active_polygon_using_real_coords(-4000, -4000)

        # apply transformation with filters
        transformation = FillNanTransformation(self.engine.get_active_model_id(),
                                               self.engine.get_active_polygon_id())
        self.engine.transform_points(transformation)

        # export model to compare data
        self.engine.export_model_as_netcdf(self.engine.get_active_model_id(),
                                           'resources/test_resources/temp/temp_transformation_3')

        # read data and compare
        info_written = read_info('resources/test_resources/temp/temp_transformation_3.nc')
        info_expected = read_info('resources/test_resources/netcdf/test_file_1.nc')

        np.testing.assert_array_almost_equal(info_written[0], info_expected[0], 3,
                                             'Info on the x array is not equal to the expected.')
        np.testing.assert_array_almost_equal(info_written[1], info_expected[1], 3,
                                             'Info on the y array is not equal to the expected.')
        np.testing.assert_array_almost_equal(info_written[2], info_expected[2], 3,
                                             'Info on the height matrix is not equal to the expected.')

        os.remove('resources/test_resources/temp/temp_transformation_3.nc')
