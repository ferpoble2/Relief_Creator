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
Module with tests related to the filters of the application.
"""
import os
import unittest
import warnings

from src.engine.scene.filter.height_greater_than import HeightGreaterThan
from src.engine.scene.filter.height_less_than import HeightLessThan
from src.engine.scene.filter.is_in import IsIn
from src.engine.scene.filter.is_not_in import IsNotIn
from src.engine.scene.transformation.linear_transformation import LinearTransformation
from src.error.filter_error import FilterError
from src.input.NetCDF import read_info
from test.test_case import ProgramTestCase


class TestIsInFilter(ProgramTestCase):

    def setUp(self) -> None:
        """
        Code executed before every test. Initializes a program to work with.
        """
        super().setUp()
        warnings.simplefilter('ignore', category=DeprecationWarning)

    def test_normal_application_is_in(self):
        self.engine.create_model_from_file('resources/test_resources/cpt/colors_0_100_200.cpt',
                                           'resources/test_resources/netcdf/test_file_50_50.nc')

        # load list of polygons
        self.engine.create_polygon_from_file('resources/test_resources/polygons/shape_three_concentric_polygons.shp')

        # apply transformation with filters
        transformation = LinearTransformation(self.engine.get_active_model_id(),
                                              'Polygon 0',
                                              100,
                                              200,
                                              [IsNotIn('Polygon 1'),
                                               IsIn('Polygon 2')])
        self.engine.apply_transformation(transformation)

        # export model to compare data
        self.engine.export_model_as_netcdf(self.engine.get_active_model_id(),
                                           'resources/test_resources/temp/temp_filter_5')

        # read data and compare
        info_written = read_info('resources/test_resources/temp/temp_filter_5.nc')
        info_expected = read_info('resources/test_resources/expected_data/netcdf/expected_filter_5.nc')

        self.assertTrue((info_written[0] == info_expected[0]).all())
        self.assertTrue((info_written[1] == info_expected[1]).all())
        self.assertTrue((info_written[2] == info_expected[2]).all())

        os.remove('resources/test_resources/temp/temp_filter_5.nc')

    def test_polygon_not_in_map_is_in_filter(self):
        self.engine.create_model_from_file('resources/test_resources/cpt/colors_0_100_200.cpt',
                                           'resources/test_resources/netcdf/test_file_50_50.nc')

        # load list of polygons
        self.engine.create_polygon_from_file('resources/test_resources/polygons/'
                                             'shape_three_polygons_south_america.shp')

        # apply transformation with filters
        transformation = LinearTransformation(self.engine.get_active_model_id(),
                                              'Polygon 0',
                                              100,
                                              200,
                                              [IsIn('Polygon 1')])
        self.engine.apply_transformation(transformation)

        # export model to compare data
        self.engine.export_model_as_netcdf(self.engine.get_active_model_id(),
                                           'resources/test_resources/temp/temp_is_in_filter_polygon_not_in_map')

        # read data and compare
        info_written = read_info('resources/test_resources/temp/temp_is_in_filter_polygon_not_in_map.nc')
        info_expected = read_info('resources/test_resources/netcdf/test_file_50_50.nc')

        self.assertTrue((info_written[0] == info_expected[0]).all())
        self.assertTrue((info_written[1] == info_expected[1]).all())
        self.assertTrue((info_written[2] == info_expected[2]).all())

        os.remove('resources/test_resources/temp/temp_is_in_filter_polygon_not_in_map.nc')

    def test_polygon_not_specified(self):
        self.engine.create_model_from_file('resources/test_resources/cpt/colors_0_100_200.cpt',
                                           'resources/test_resources/netcdf/test_file_50_50.nc')
        self.engine.create_polygon_from_file('resources/test_resources/polygons/'
                                             'shape_three_polygons_south_america.shp')

        transformation = LinearTransformation(self.engine.get_active_model_id(),
                                              'Polygon 0',
                                              100,
                                              200,
                                              [IsIn(None)])
        with self.assertRaises(FilterError) as e:
            transformation.initialize(self.engine.scene)
            transformation.apply()
        self.assertEqual(0, e.exception.code, 'Exception code is not 0')

    def test_polygon_not_existent(self):
        self.engine.create_model_from_file('resources/test_resources/cpt/colors_0_100_200.cpt',
                                           'resources/test_resources/netcdf/test_file_50_50.nc')
        self.engine.create_polygon_from_file('resources/test_resources/polygons/'
                                             'shape_three_polygons_south_america.shp')

        transformation = LinearTransformation(self.engine.get_active_model_id(),
                                              'Polygon 0',
                                              100,
                                              200,
                                              [IsIn('Another polygon not in the program.')])
        with self.assertRaises(FilterError) as e:
            transformation.initialize(self.engine.scene)
            transformation.apply()
        self.assertEqual(3, e.exception.code, 'Exception code is not 3')

    def test_polygon_not_planar(self):
        self.engine.create_model_from_file('resources/test_resources/cpt/colors_0_100_200.cpt',
                                           'resources/test_resources/netcdf/test_file_50_50.nc')
        self.engine.create_polygon_from_file('resources/test_resources/polygons/'
                                             'shape_three_polygons_south_america.shp')

        polygon_not_planar = self.engine.create_new_polygon()
        self.engine.set_active_polygon(polygon_not_planar)
        self.engine.add_new_vertex_to_active_polygon_using_real_coords(10, 10)
        self.engine.add_new_vertex_to_active_polygon_using_real_coords(20, 10)
        self.engine.add_new_vertex_to_active_polygon_using_real_coords(10, 20)
        self.engine.add_new_vertex_to_active_polygon_using_real_coords(20, 20)

        transformation = LinearTransformation(self.engine.get_active_model_id(),
                                              'Polygon 0',
                                              100,
                                              200,
                                              [IsIn(polygon_not_planar)])
        with self.assertRaises(FilterError) as e:
            transformation.initialize(self.engine.scene)
            transformation.apply()
        self.assertEqual(2, e.exception.code, 'Exception code is not 2.')

    def test_polygon_not_enough_points(self):
        self.engine.create_model_from_file('resources/test_resources/cpt/colors_0_100_200.cpt',
                                           'resources/test_resources/netcdf/test_file_50_50.nc')
        self.engine.create_polygon_from_file('resources/test_resources/polygons/'
                                             'shape_three_polygons_south_america.shp')

        polygon_not_enough_points = self.engine.create_new_polygon()
        self.engine.set_active_polygon(polygon_not_enough_points)
        self.engine.add_new_vertex_to_active_polygon_using_real_coords(10, 10)

        transformation = LinearTransformation(self.engine.get_active_model_id(),
                                              'Polygon 0',
                                              100,
                                              200,
                                              [IsIn(polygon_not_enough_points)])
        with self.assertRaises(FilterError) as e:
            transformation.initialize(self.engine.scene)
            transformation.apply()
        self.assertEqual(1, e.exception.code, 'Exception code is not 1')


class TestIsNotInFilter(ProgramTestCase):

    def setUp(self) -> None:
        """
        Code executed before every test. Initializes a program to work with.
        """
        super().setUp()
        warnings.simplefilter('ignore', category=DeprecationWarning)

    def test_normal_application_is_not_in(self):
        self.engine.create_model_from_file('resources/test_resources/cpt/colors_0_100_200.cpt',
                                           'resources/test_resources/netcdf/test_file_50_50.nc')

        # load list of polygons
        self.engine.create_polygon_from_file('resources/test_resources/polygons/shape_two_concentric_polygons.shp')

        # apply transformation with filters
        transformation = LinearTransformation(self.engine.get_active_model_id(),
                                              'Polygon 0',
                                              100,
                                              200,
                                              [IsNotIn('Polygon 1')])
        self.engine.apply_transformation(transformation)

        # export model to compare data
        self.engine.export_model_as_netcdf(self.engine.get_active_model_id(),
                                           'resources/test_resources/temp/temp_filter_6')

        # read data and compare
        info_written = read_info('resources/test_resources/temp/temp_filter_6.nc')
        info_expected = read_info('resources/test_resources/expected_data/netcdf/expected_filter_6.nc')

        self.assertTrue((info_written[0] == info_expected[0]).all())
        self.assertTrue((info_written[1] == info_expected[1]).all())
        self.assertTrue((info_written[2] == info_expected[2]).all())

        os.remove('resources/test_resources/temp/temp_filter_6.nc')

    def test_polygon_not_in_map_is_not_in_filter(self):
        self.engine.create_model_from_file('resources/test_resources/cpt/colors_0_100_200.cpt',
                                           'resources/test_resources/netcdf/test_file_50_50.nc')

        # load list of polygons
        self.engine.create_polygon_from_file('resources/test_resources/polygons/'
                                             'shape_three_polygons_south_america.shp')

        # apply transformation with filters
        transformation = LinearTransformation(self.engine.get_active_model_id(),
                                              'Polygon 0',
                                              100,
                                              200,
                                              [IsNotIn('Polygon 1'),
                                               IsIn('Polygon 2')])
        self.engine.apply_transformation(transformation)

        # export model to compare data
        self.engine.export_model_as_netcdf(self.engine.get_active_model_id(),
                                           'resources/test_resources/temp/temp_is_in_filter_polygon_not_in_map')

        # read data and compare
        info_written = read_info('resources/test_resources/temp/temp_is_in_filter_polygon_not_in_map.nc')
        info_expected = read_info('resources/test_resources/netcdf/test_file_50_50.nc')

        self.assertTrue((info_written[0] == info_expected[0]).all())
        self.assertTrue((info_written[1] == info_expected[1]).all())
        self.assertTrue((info_written[2] == info_expected[2]).all())

        os.remove('resources/test_resources/temp/temp_is_in_filter_polygon_not_in_map.nc')

    def test_polygon_not_specified(self):
        self.engine.create_model_from_file('resources/test_resources/cpt/colors_0_100_200.cpt',
                                           'resources/test_resources/netcdf/test_file_50_50.nc')
        self.engine.create_polygon_from_file('resources/test_resources/polygons/'
                                             'shape_three_polygons_south_america.shp')

        transformation = LinearTransformation(self.engine.get_active_model_id(),
                                              'Polygon 0',
                                              100,
                                              200,
                                              [IsNotIn(None)])
        with self.assertRaises(FilterError) as e:
            transformation.initialize(self.engine.scene)
            transformation.apply()
        self.assertEqual(0, e.exception.code, 'Exception code is not 0')

    def test_polygon_not_existent(self):
        self.engine.create_model_from_file('resources/test_resources/cpt/colors_0_100_200.cpt',
                                           'resources/test_resources/netcdf/test_file_50_50.nc')
        self.engine.create_polygon_from_file('resources/test_resources/polygons/'
                                             'shape_three_polygons_south_america.shp')

        transformation = LinearTransformation(self.engine.get_active_model_id(),
                                              'Polygon 0',
                                              100,
                                              200,
                                              [IsNotIn('Another polygon not in the program.')])
        with self.assertRaises(FilterError) as e:
            transformation.initialize(self.engine.scene)
            transformation.apply()
        self.assertEqual(3, e.exception.code, 'Exception code is not 3')

    def test_polygon_not_planar(self):
        self.engine.create_model_from_file('resources/test_resources/cpt/colors_0_100_200.cpt',
                                           'resources/test_resources/netcdf/test_file_50_50.nc')
        self.engine.create_polygon_from_file('resources/test_resources/polygons/'
                                             'shape_three_polygons_south_america.shp')

        polygon_not_planar = self.engine.create_new_polygon()
        self.engine.set_active_polygon(polygon_not_planar)
        self.engine.add_new_vertex_to_active_polygon_using_real_coords(10, 10)
        self.engine.add_new_vertex_to_active_polygon_using_real_coords(20, 10)
        self.engine.add_new_vertex_to_active_polygon_using_real_coords(10, 20)
        self.engine.add_new_vertex_to_active_polygon_using_real_coords(20, 20)

        transformation = LinearTransformation(self.engine.get_active_model_id(),
                                              'Polygon 0',
                                              100,
                                              200,
                                              [IsNotIn(polygon_not_planar)])
        with self.assertRaises(FilterError) as e:
            transformation.initialize(self.engine.scene)
            transformation.apply()
        self.assertEqual(2, e.exception.code, 'Exception code is not 2.')

    def test_polygon_not_enough_points(self):
        self.engine.create_model_from_file('resources/test_resources/cpt/colors_0_100_200.cpt',
                                           'resources/test_resources/netcdf/test_file_50_50.nc')
        self.engine.create_polygon_from_file('resources/test_resources/polygons/'
                                             'shape_three_polygons_south_america.shp')

        polygon_not_enough_points = self.engine.create_new_polygon()
        self.engine.set_active_polygon(polygon_not_enough_points)
        self.engine.add_new_vertex_to_active_polygon_using_real_coords(10, 10)

        transformation = LinearTransformation(self.engine.get_active_model_id(),
                                              'Polygon 0',
                                              100,
                                              200,
                                              [IsNotIn(polygon_not_enough_points)])
        with self.assertRaises(FilterError) as e:
            transformation.initialize(self.engine.scene)
            transformation.apply()
        self.assertEqual(1, e.exception.code, 'Exception code is not 1')


class TestGreaterThanFilter(ProgramTestCase):

    def setUp(self) -> None:
        """
        Code executed before every test. Initializes a program to work with.
        """
        super().setUp()
        warnings.simplefilter('ignore', category=DeprecationWarning)

    def test_normal_application_greater_than(self):
        self.engine.create_model_from_file('resources/test_resources/cpt/colors_0_100_200.cpt',
                                           'resources/test_resources/netcdf/test_file_50_50.nc')

        # load polygon
        self.engine.create_polygon_from_file('resources/test_resources/polygons/shape_one_polygon_2.shp')

        # create polygon to modify the scene.
        transformation = LinearTransformation(self.engine.get_active_model_id(),
                                              self.engine.get_active_polygon_id(),
                                              100,
                                              200,
                                              [HeightGreaterThan(50)])
        self.engine.apply_transformation(transformation)

        # export model to compare data
        self.engine.export_model_as_netcdf(self.engine.get_active_model_id(),
                                           'resources/test_resources/temp/temp_filter_4')

        # read data and compare
        info_written = read_info('resources/test_resources/temp/temp_filter_4.nc')
        info_expected = read_info('resources/test_resources/expected_data/netcdf/expected_filter_4.nc')

        self.assertTrue((info_written[0] == info_expected[0]).all())
        self.assertTrue((info_written[1] == info_expected[1]).all())
        self.assertTrue((info_written[2] == info_expected[2]).all())

        os.remove('resources/test_resources/temp/temp_filter_4.nc')

    def test_polygon_not_in_map(self):
        self.engine.create_model_from_file('resources/test_resources/cpt/colors_0_100_200.cpt',
                                           'resources/test_resources/netcdf/test_file_50_50.nc')

        # load list of polygons
        self.engine.create_polygon_from_file('resources/test_resources/polygons/'
                                             'shape_three_polygons_south_america.shp')

        # apply transformation with filters
        transformation = LinearTransformation(self.engine.get_active_model_id(),
                                              self.engine.get_active_polygon_id(),
                                              100,
                                              200,
                                              [HeightGreaterThan(0)])
        self.engine.apply_transformation(transformation)

        # export model to compare data
        self.engine.export_model_as_netcdf(self.engine.get_active_model_id(),
                                           'resources/test_resources/temp/temp_is_in_filter_polygon_not_in_map')

        # read data and compare
        info_written = read_info('resources/test_resources/temp/temp_is_in_filter_polygon_not_in_map.nc')
        info_expected = read_info('resources/test_resources/netcdf/test_file_50_50.nc')

        self.assertTrue((info_written[0] == info_expected[0]).all())
        self.assertTrue((info_written[1] == info_expected[1]).all())
        self.assertTrue((info_written[2] == info_expected[2]).all())

        os.remove('resources/test_resources/temp/temp_is_in_filter_polygon_not_in_map.nc')


class TestLessThanFilter(ProgramTestCase):

    def setUp(self) -> None:
        """
        Code executed before every test. Initializes a program to work with.
        """
        super().setUp()
        warnings.simplefilter('ignore', category=DeprecationWarning)

    def test_normal_application_less_than(self):
        self.engine.create_model_from_file('resources/test_resources/cpt/colors_0_100_200.cpt',
                                           'resources/test_resources/netcdf/test_file_50_50.nc')

        # load polygon
        self.engine.create_polygon_from_file('resources/test_resources/polygons/shape_one_polygon_2.shp')

        # create polygon to modify the scene.
        transformation = LinearTransformation(self.engine.get_active_model_id(),
                                              self.engine.get_active_polygon_id(),
                                              100,
                                              200,
                                              [HeightLessThan(50)])
        self.engine.apply_transformation(transformation)

        # export model to compare data
        self.engine.export_model_as_netcdf(self.engine.get_active_model_id(),
                                           'resources/test_resources/temp/temp_filter_3')

        # read data and compare
        info_written = read_info('resources/test_resources/temp/temp_filter_3.nc')
        info_expected = read_info('resources/test_resources/expected_data/netcdf/expected_filter_3.nc')

        self.assertTrue((info_written[0] == info_expected[0]).all())
        self.assertTrue((info_written[1] == info_expected[1]).all())
        self.assertTrue((info_written[2] == info_expected[2]).all())

        os.remove('resources/test_resources/temp/temp_filter_3.nc')

    def test_polygon_not_in_map(self):
        self.engine.create_model_from_file('resources/test_resources/cpt/colors_0_100_200.cpt',
                                           'resources/test_resources/netcdf/test_file_50_50.nc')

        # load list of polygons
        self.engine.create_polygon_from_file('resources/test_resources/polygons/'
                                             'shape_three_polygons_south_america.shp')

        # apply transformation with filters
        transformation = LinearTransformation(self.engine.get_active_model_id(),
                                              self.engine.get_active_polygon_id(),
                                              100,
                                              200,
                                              [HeightLessThan(3000)])
        self.engine.apply_transformation(transformation)

        # export model to compare data
        self.engine.export_model_as_netcdf(self.engine.get_active_model_id(),
                                           'resources/test_resources/temp/temp_is_in_filter_polygon_not_in_map')

        # read data and compare
        info_written = read_info('resources/test_resources/temp/temp_is_in_filter_polygon_not_in_map.nc')
        info_expected = read_info('resources/test_resources/netcdf/test_file_50_50.nc')

        self.assertTrue((info_written[0] == info_expected[0]).all())
        self.assertTrue((info_written[1] == info_expected[1]).all())
        self.assertTrue((info_written[2] == info_expected[2]).all())

        os.remove('resources/test_resources/temp/temp_is_in_filter_polygon_not_in_map.nc')


class TestMixedFilters(ProgramTestCase):

    def setUp(self) -> None:
        """
        Code executed before every test. Initializes a program to work with.
        """
        super().setUp()
        warnings.simplefilter('ignore', category=DeprecationWarning)

    def test_height_contain(self):
        self.engine.create_model_from_file('resources/test_resources/cpt/cpt_1.cpt',
                                           'resources/test_resources/netcdf/test_file_1.nc')

        # load polygon
        self.engine.create_polygon_from_file('resources/test_resources/polygons/'
                                             'shape_three_polygons_south_america.shp')

        # create polygon to modify the scene.
        transformation = LinearTransformation(self.engine.get_active_model_id(),
                                              'Polygon 0',
                                              800,
                                              2500,
                                              [HeightGreaterThan(0),
                                               HeightLessThan(5800),
                                               IsNotIn('Polygon 2'),
                                               IsIn('Polygon 1')])
        self.engine.apply_transformation(transformation)

        # export model to compare data
        self.engine.export_model_as_netcdf(self.engine.get_active_model_id(),
                                           'resources/test_resources/temp/temp_transformation_mixed')

        # read data and compare
        info_written = read_info('resources/test_resources/temp/temp_transformation_mixed.nc')
        info_expected = read_info('resources/test_resources/expected_data/netcdf/expected_transformation_2.nc')

        self.assertTrue((info_written[0] == info_expected[0]).all())
        self.assertTrue((info_written[1] == info_expected[1]).all())
        self.assertTrue((info_written[2] == info_expected[2]).all())

        os.remove('resources/test_resources/temp/temp_transformation_mixed.nc')


if __name__ == '__main__':
    unittest.main()
