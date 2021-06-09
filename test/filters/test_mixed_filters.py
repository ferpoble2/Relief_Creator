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
File with tests that mix different filters at the same time to modify a map.
"""

import unittest
import os
import warnings

from src.engine.engine import Engine
from src.program.program import Program
from src.input.NetCDF import read_info


class TestMixedFilters(unittest.TestCase):

    def setUp(self) -> None:
        """
        Code executed before every test. Initializes a program to work with.
        """

        # create program
        self.engine = Engine()
        self.program = Program(self.engine)

        # initialize variables
        self.engine.should_use_threads(False)

    def test_non_existent_filter(self):
        warnings.simplefilter("ignore", ResourceWarning)

        self.engine.load_netcdf_file('resources/test_resources/cpt/cpt_1.cpt',
                                          'resources/test_resources/netcdf/test_file_1.nc')

        # load polygon
        self.engine.load_polygon_from_shapefile('resources/test_resources/polygons/'
                                                'shape_three_polygons_south_america.shp')

        # create polygon to modify the scene.
        with self.assertRaises(NotImplementedError):
            self.engine.transform_points(polygon_id='Polygon 0',
                                         model_id=self.engine.get_active_model_id(),
                                         min_height=800,
                                         max_height=2500,
                                         transformation_type='linear',
                                         filters=[('Non_existent_filter', 0)])

        with self.assertRaises(NotImplementedError):
            self.engine.transform_points(polygon_id='Polygon 0',
                                         model_id=self.engine.get_active_model_id(),
                                         min_height=800,
                                         max_height=2500,
                                         transformation_type='linear',
                                         filters=[('height_greater_than', 0),
                                                  ('height_less_than', 5800),
                                                  ('Non_existent_filter', 'Polygon 2'),
                                                  ('is_in', 'Polygon 1')])

    def test_height_contain(self):
        warnings.simplefilter("ignore", ResourceWarning)

        self.engine.load_netcdf_file('resources/test_resources/cpt/cpt_1.cpt',
                                          'resources/test_resources/netcdf/test_file_1.nc')

        # load polygon
        self.engine.load_polygon_from_shapefile('resources/test_resources/polygons/'
                                                'shape_three_polygons_south_america.shp')

        # create polygon to modify the scene.
        self.engine.transform_points(polygon_id='Polygon 0',
                                     model_id=self.engine.get_active_model_id(),
                                     min_height=800,
                                     max_height=2500,
                                     transformation_type='linear',
                                     filters=[('height_greater_than', 0),
                                              ('height_less_than', 5800),
                                              ('is_not_in', 'Polygon 2'),
                                              ('is_in', 'Polygon 1')])

        # export model to compare data
        self.engine.export_model_as_netcdf(self.engine.get_active_model_id(),
                                           'resources/test_resources/temp/temp_transformation_mixed')

        # read data and compare
        info_written = read_info('resources/test_resources/temp/temp_transformation_mixed.nc')
        info_expected = read_info('resources/test_resources/expected_data/netcdf/expected_transformation_2.nc.nc')

        self.assertTrue((info_written[0] == info_expected[0]).all())
        self.assertTrue((info_written[1] == info_expected[1]).all())
        self.assertTrue((info_written[2] == info_expected[2]).all())

        os.remove('resources/test_resources/temp/temp_transformation_mixed.nc')


if __name__ == '__main__':
    unittest.main()
