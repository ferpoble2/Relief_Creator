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
File with the tests related to the functionality that applies height filters to the polygons.
"""
import unittest
import warnings
import os

from src.engine.engine import Engine
from src.program.program import Program
from src.input.NetCDF import read_info


class TestHeightGreaterFilter(unittest.TestCase):

    def setUp(self) -> None:
        """
        Code executed before every test. Initializes a program to work with.
        """

        # create program
        self.engine = Engine()
        self.program = Program(self.engine)

        # initialize variables
        self.engine.should_use_threads(False)

    def test_normal_application_less_than(self):
        warnings.simplefilter("ignore", ResourceWarning)

        self.engine.load_netcdf_file('resources/test_resources/cpt/colors_0_100_200.cpt',
                                          'resources/test_resources/netcdf/test_file_50_50.nc')

        # load polygon
        self.engine.load_polygon_from_shapefile('resources/test_resources/polygons/shape_one_polygon_2.shp')

        # create polygon to modify the scene.
        self.engine.transform_points(polygon_id=self.engine.get_active_polygon_id(),
                                     model_id=self.engine.get_active_model_id(),
                                     min_height=100,
                                     max_height=200,
                                     transformation_type='linear',
                                     filters=[('height_less_than', 50)])

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

    def test_normal_application_greater_than(self):
        warnings.simplefilter("ignore", ResourceWarning)

        self.engine.load_netcdf_file('resources/test_resources/cpt/colors_0_100_200.cpt',
                                          'resources/test_resources/netcdf/test_file_50_50.nc')

        # load polygon
        self.engine.load_polygon_from_shapefile('resources/test_resources/polygons/shape_one_polygon_2.shp')

        # create polygon to modify the scene.
        self.engine.transform_points(polygon_id=self.engine.get_active_polygon_id(),
                                     model_id=self.engine.get_active_model_id(),
                                     min_height=100,
                                     max_height=200,
                                     transformation_type='linear',
                                     filters=[('height_greater_than', 50)])

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

    def test_filters_not_in_map(self):
        warnings.simplefilter("ignore", ResourceWarning)

        self.engine.load_netcdf_file('resources/test_resources/cpt/colors_0_100_200.cpt',
                                          'resources/test_resources/netcdf/test_file_50_50.nc')

        # load list of polygons
        self.engine.load_polygon_from_shapefile('resources/test_resources/polygons/'
                                                'shape_three_polygons_south_america.shp')

        # apply transformation with filters
        self.engine.transform_points(polygon_id='Polygon 0',
                                     model_id=self.engine.get_active_model_id(),
                                     min_height=100,
                                     max_height=200,
                                     transformation_type='linear',
                                     filters=[('height_greater_than', 0),
                                              ('height_less_than', 3000)])

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

if __name__ == '__main__':
    unittest.main()
