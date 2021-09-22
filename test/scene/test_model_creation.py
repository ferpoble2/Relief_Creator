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
Module to tests the creation of models on the scene.
"""
import os
import unittest

import numpy as np

from src.input.NetCDF import read_info
from src.program.program import Program


class TestCreateModelFromExistent(unittest.TestCase):

    def test_creation_model(self):
        program = Program()
        engine = program.engine
        engine.should_use_threads(False)

        engine.create_model_from_file('resources/test_resources/cpt/colors_0_100_200.cpt',
                                      'resources/test_resources/netcdf/test_model_3.nc')
        engine.create_model_from_file('resources/test_resources/cpt/colors_0_100_200.cpt',
                                      'resources/test_resources/netcdf/test_model_4.nc')

        engine.create_model_from_existent('0', '1', 'new_model')
        engine.export_model_as_netcdf('2', 'resources/test_resources/temp/combined_model_test.nc')

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

        program.close()
        os.remove('resources/test_resources/temp/combined_model_test.nc')
