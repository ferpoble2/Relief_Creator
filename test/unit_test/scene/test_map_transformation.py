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
Module in charge of the testing of the modification done by the map transformations.
"""

import os
import unittest
import warnings

import numpy as np

from src.engine.scene.map_transformation.fill_nan_map_transformation import FillNanMapTransformation
from src.engine.scene.map_transformation.interpolate_nan_map_transformation import InterpolateNanMapTransformation, \
    InterpolateNanMapTransformationType
from src.engine.scene.map_transformation.merge_maps_transformation import MergeMapsTransformation
from src.error.map_transformation_error import MapTransformationError
from src.input.NetCDF import read_info
from test.test_case import ProgramTestCase


class TestMergeMapsTransformation(ProgramTestCase):

    def test_merge_maps(self):
        self.engine.create_model_from_file('resources/test_resources/cpt/colors_0_100_200.cpt',
                                           'resources/test_resources/netcdf/test_model_3.nc')
        self.engine.create_model_from_file('resources/test_resources/cpt/colors_0_100_200.cpt',
                                           'resources/test_resources/netcdf/test_model_4.nc')

        map_transformation = MergeMapsTransformation('0', '1')
        self.engine.apply_map_transformation(map_transformation)
        self.engine.export_model_as_netcdf('0', 'resources/test_resources/temp/combined_model_test.nc')

        x, y, z = read_info('resources/test_resources/temp/combined_model_test.nc')
        expected_x, expected_y, expected_z = read_info(
            'resources/test_resources/expected_data/netcdf/expected_combined.nc')

        np.testing.assert_array_equal(expected_x,
                                      x,
                                      "x array stored is not the same as the expected.")
        np.testing.assert_array_equal(expected_y,
                                      y,
                                      "y array stored is not the same as the expected.")
        np.testing.assert_array_equal(expected_z,
                                      z,
                                      "heights stored are not equal to the expected.")

        os.remove('resources/test_resources/temp/combined_model_test.nc')

    def test_bad_map_arguments(self):
        self.engine.create_model_from_file('resources/test_resources/cpt/colors_0_100_200.cpt',
                                           'resources/test_resources/netcdf/test_model_3.nc')

        map_transformation_secondary_error = MergeMapsTransformation('0', '1')
        with self.assertRaises(MapTransformationError) as e:
            map_transformation_secondary_error.initialize(self.engine.scene)
            map_transformation_secondary_error.apply()
        self.assertEqual(1, e.exception.code, 'Exception error code is not 1.')

        map_transformation_base_error = MergeMapsTransformation('1', '0')
        with self.assertRaises(MapTransformationError) as e:
            map_transformation_base_error.initialize(self.engine.scene)
            map_transformation_base_error.apply()
        self.assertEqual(1, e.exception.code, 'Exception error code is not 1')


class TestFillNanTransformation(ProgramTestCase):

    def setUp(self) -> None:
        """Setup parameters before each test"""
        super().setUp()
        warnings.simplefilter('ignore', DeprecationWarning)

    def test_fill_nan_one_polygon(self):
        self.engine.create_model_from_file('resources/test_resources/cpt/colors_0_100_200.cpt',
                                           'resources/test_resources/netcdf/test_file_1.nc')
        self.engine.create_polygon_from_file('resources/test_resources/polygons/shape_one_polygon.shp')

        map_transformation = FillNanMapTransformation(self.engine.get_active_model_id())
        self.engine.apply_map_transformation(map_transformation)
        self.engine.export_model_as_netcdf(self.engine.get_active_model_id(),
                                           'resources/test_resources/temp/fill_nan_one_polygon.nc')

        x, y, z = read_info('resources/test_resources/temp/fill_nan_one_polygon.nc')
        expected_x, expected_y, expected_z = read_info(
            'resources/test_resources/expected_data/netcdf/expected_map_transformation_1.nc')

        np.testing.assert_array_equal(expected_x,
                                      x,
                                      "x array stored is not the same as the expected.")
        np.testing.assert_array_equal(expected_y,
                                      y,
                                      "y array stored is not the same as the expected.")
        np.testing.assert_array_equal(expected_z,
                                      z,
                                      "heights stored are not equal to the expected.")

        os.remove('resources/test_resources/temp/fill_nan_one_polygon.nc')

    def test_fill_nan_multiple_polygon(self):
        self.engine.create_model_from_file('resources/test_resources/cpt/colors_0_100_200.cpt',
                                           'resources/test_resources/netcdf/test_file_1.nc')
        self.engine.create_polygon_from_file('resources/test_resources/polygons/shape_many_polygons.shp')

        map_transformation = FillNanMapTransformation(self.engine.get_active_model_id())
        self.engine.apply_map_transformation(map_transformation)
        self.engine.export_model_as_netcdf(self.engine.get_active_model_id(),
                                           'resources/test_resources/temp/fill_nan_multiple_polygon.nc')

        x, y, z = read_info('resources/test_resources/temp/fill_nan_multiple_polygon.nc')
        expected_x, expected_y, expected_z = read_info(
            'resources/test_resources/expected_data/netcdf/expected_map_transformation_2.nc')

        np.testing.assert_array_equal(expected_x,
                                      x,
                                      "x array stored is not the same as the expected.")
        np.testing.assert_array_equal(expected_y,
                                      y,
                                      "y array stored is not the same as the expected.")
        np.testing.assert_array_equal(expected_z,
                                      z,
                                      "heights stored are not equal to the expected.")

        os.remove('resources/test_resources/temp/fill_nan_multiple_polygon.nc')

    def test_fill_nan_polygon_outside(self):
        self.engine.create_model_from_file('resources/test_resources/cpt/colors_0_100_200.cpt',
                                           'resources/test_resources/netcdf/test_file_1.nc')

        polygon_id = self.engine.create_new_polygon()
        self.engine.add_new_vertex_to_active_polygon_using_real_coords(-5000, -5000)
        self.engine.add_new_vertex_to_active_polygon_using_real_coords(-5000, -4000)
        self.engine.add_new_vertex_to_active_polygon_using_real_coords(-4000, -4000)

        map_transformation = FillNanMapTransformation(self.engine.get_active_model_id())
        self.engine.apply_map_transformation(map_transformation)
        self.engine.export_model_as_netcdf(self.engine.get_active_model_id(),
                                           'resources/test_resources/temp/fill_polygon_outside.nc')

        x, y, z = read_info('resources/test_resources/temp/fill_polygon_outside.nc')
        expected_x, expected_y, expected_z = read_info('resources/test_resources/netcdf/test_file_1.nc')

        np.testing.assert_array_equal(expected_x,
                                      x,
                                      "x array stored is not the same as the expected.")
        np.testing.assert_array_equal(expected_y,
                                      y,
                                      "y array stored is not the same as the expected.")
        np.testing.assert_array_equal(expected_z,
                                      z,
                                      "heights stored are not equal to the expected.")

        os.remove('resources/test_resources/temp/fill_polygon_outside.nc')

    def test_bad_arguments(self):
        map_transformation = FillNanMapTransformation('NonExistentModel')
        with self.assertRaises(MapTransformationError) as e:
            map_transformation.initialize(self.engine.scene)
            map_transformation.apply()
        self.assertEqual(1, e.exception.code, 'Exception code is not 1')

    def test_no_polygons(self):
        self.engine.create_model_from_file('resources/test_resources/cpt/colors_0_100_200.cpt',
                                           'resources/test_resources/netcdf/test_file_1.nc')

        map_transformation = FillNanMapTransformation(self.engine.get_active_model_id())
        self.engine.apply_map_transformation(map_transformation)
        self.engine.export_model_as_netcdf(self.engine.get_active_model_id(),
                                           'resources/test_resources/temp/fill_polygon_outside.nc')

        x, y, z = read_info('resources/test_resources/temp/fill_polygon_outside.nc')
        expected_x, expected_y, expected_z = read_info('resources/test_resources/netcdf/test_file_1.nc')

        np.testing.assert_array_equal(expected_x,
                                      x,
                                      "x array stored is not the same as the expected.")
        np.testing.assert_array_equal(expected_y,
                                      y,
                                      "y array stored is not the same as the expected.")
        np.testing.assert_array_equal(expected_z,
                                      z,
                                      "heights stored are not equal to the expected.")

        os.remove('resources/test_resources/temp/fill_polygon_outside.nc')


class TestInterpolateNanMapTransformation(ProgramTestCase):

    def setUp(self) -> None:
        """Logic executed before every test."""
        super().setUp()
        self.engine.create_model_from_file('resources/test_resources/cpt/colors_0_100_200.cpt',
                                           'resources/test_resources/netcdf/test_data_nan_values.nc')

    def test_cubic_transformation(self):
        # Apply transformation
        # --------------------
        map_transformation = InterpolateNanMapTransformation(self.engine.get_active_model_id(),
                                                             InterpolateNanMapTransformationType.cubic)
        self.engine.apply_map_transformation(map_transformation)
        self.engine.export_model_as_netcdf(self.engine.get_active_model_id(),
                                           'resources/test_resources/temp/interpolate_nan_map_3.nc')

        # Check values
        # ------------
        self.check_map_values('resources/test_resources/temp/interpolate_nan_map_3.nc',
                              'resources/test_resources/expected_data/netcdf/expected_map_transformation_5.nc')

        os.remove('resources/test_resources/temp/interpolate_nan_map_3.nc')

    def test_nearest_transformation(self):
        # Apply transformation
        # --------------------
        map_transformation = InterpolateNanMapTransformation(self.engine.get_active_model_id(),
                                                             InterpolateNanMapTransformationType.nearest)
        self.engine.apply_map_transformation(map_transformation)
        self.engine.export_model_as_netcdf(self.engine.get_active_model_id(),
                                           'resources/test_resources/temp/interpolate_nan_map_2.nc')

        # Check values
        # ------------
        self.check_map_values('resources/test_resources/temp/interpolate_nan_map_2.nc',
                              'resources/test_resources/expected_data/netcdf/expected_map_transformation_4.nc')

        os.remove('resources/test_resources/temp/interpolate_nan_map_2.nc')

    def test_linear_transformation(self):
        # Apply transformation
        # --------------------
        map_transformation = InterpolateNanMapTransformation(self.engine.get_active_model_id(),
                                                             InterpolateNanMapTransformationType.linear)
        self.engine.apply_map_transformation(map_transformation)
        self.engine.export_model_as_netcdf(self.engine.get_active_model_id(),
                                           'resources/test_resources/temp/interpolate_nan_map_1.nc')

        # Check values
        # ------------
        self.check_map_values('resources/test_resources/temp/interpolate_nan_map_1.nc',
                              'resources/test_resources/expected_data/netcdf/expected_map_transformation_3.nc')

        os.remove('resources/test_resources/temp/interpolate_nan_map_1.nc')

    def check_map_values(self, generated_file: str, expected_data_file: str) -> None:
        """
        Check the data from a generated netcdf file and the data in the expected_data_file.

        Asserts used are the ones defined in teh numpy.testing library.

        Args:
            generated_file: Netcdf file with the data to check.
            expected_data_file: Netcdf file with the expected data from the generated file.

        Returns: None
        """
        x, y, z = read_info(generated_file)
        expected_x, expected_y, expected_z = read_info(expected_data_file)
        np.testing.assert_array_equal(expected_x,
                                      x,
                                      "x array stored is not the same as the expected.")
        np.testing.assert_array_equal(expected_y,
                                      y,
                                      "y array stored is not the same as the expected.")
        np.testing.assert_array_equal(expected_z,
                                      z,
                                      "heights stored are not equal to the expected.")


if __name__ == '__main__':
    unittest.main()
