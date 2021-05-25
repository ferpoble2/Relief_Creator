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

import unittest
import warnings
import os

from src.engine.engine import Engine
from src.program.program import Program
from src.input.NetCDF import read_info


class TestModifyHeight(unittest.TestCase):

    def setUp(self) -> None:
        """
        Logic that runs at the beginning o every tests.

        Returns: None
        """
        warnings.simplefilter("ignore", ResourceWarning)

        # create program
        self.engine = Engine()
        self.program = Program(self.engine)

        # initialize variables
        self.engine.should_use_threads(False)
        self.engine.refresh_with_model_2d('resources/test_resources/cpt/cpt_1.cpt',
                                          'resources/test_resources/netcdf/test_model_2.nc')

    def test_linear_transformation(self):
        warnings.simplefilter("ignore", ResourceWarning)

        self.engine.refresh_with_model_2d('resources/test_resources/cpt/cpt_1.cpt',
                                          'resources/test_resources/netcdf/test_file_1.nc')

        # load list of polygons
        self.engine.load_polygon_from_shapefile('resources/test_resources/polygons/shape_one_polygon_south_america.shp')

        # apply transformation with filters
        self.engine.transform_points(polygon_id=self.engine.get_active_polygon_id(),
                                     model_id=self.engine.get_active_model_id(),
                                     min_height=2000,
                                     max_height=3000,
                                     transformation_type='linear',
                                     filters=[])

        # export model to compare data
        self.engine.export_model_as_netcdf(self.engine.get_active_model_id(),
                                           'resources/test_resources/temp/temp_transformation_1')

        # read data and compare
        info_written = read_info('resources/test_resources/temp/temp_transformation_1.nc')
        info_expected = read_info('resources/test_resources/expected_data/netcdf/expected_transformation_1.nc')

        self.assertTrue((info_written[0] == info_expected[0]).all(),
                        'Info on the x array is not equal to the expected.')
        self.assertTrue((info_written[1] == info_expected[1]).all(),
                        'Info on the y array is not equal to the expected.')
        self.assertTrue((info_written[2] == info_expected[2]).all(),
                        'Info on the height matrix is not equal to the expected.')

        os.remove('resources/test_resources/temp/temp_transformation_1.nc')
