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
import warnings

import numpy as np
import psutil

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


class Test3DModelCreationMemoryUsageOneModel(unittest.TestCase):

    def remove_all_models(self):
        """
        Remove all the models from the program.
        """
        for model_id in self.engine.get_model_list():
            self.engine.remove_model(model_id)

    def load_3d_model(self):
        """Load a new 3D model on the program."""
        self.program.set_view_mode_3D()
        self.engine.create_model_from_file('resources/test_resources/cpt/colors_0_100_200.cpt',
                                           'resources/test_resources/netcdf/test_file_1.nc')
        self.engine.run(5, False)

    def setUp(self) -> None:
        """Initialize the variables for the tests"""
        warnings.simplefilter("ignore", ResourceWarning)

        self.program = Program()
        self.engine = self.program.engine
        self.engine.should_use_threads(False)

    def tearDown(self) -> None:
        """Close the program"""
        self.program.close()

    def test_memory_usage_3D_models(self):
        process = psutil.Process(os.getpid())
        initial_memory_usage = self.get_memory_usage_in_megabytes(process)

        self.load_3d_model()
        memory_usage_one_model = self.get_memory_usage_in_megabytes(process)
        self.assertLess(memory_usage_one_model - initial_memory_usage,
                        600,
                        "Memory usage is not less than 600 Megabytes when loading a four 3D model.")

        self.load_3d_model()
        memory_usage_two_models = self.get_memory_usage_in_megabytes(process)
        self.assertLess(memory_usage_two_models - initial_memory_usage,
                        900,
                        "Memory usage is not less than 900 Megabytes when loading a four 3D model.")

        self.load_3d_model()
        memory_usage_three_models = self.get_memory_usage_in_megabytes(process)
        self.assertLess(memory_usage_three_models - initial_memory_usage,
                        1150,
                        "Memory usage is not less than 1150 Megabytes when loading a four 3D model.")

        self.load_3d_model()
        memory_usage_four_models = self.get_memory_usage_in_megabytes(process)
        self.assertLess(memory_usage_four_models - initial_memory_usage,
                        1500,
                        "Memory usage is not less than 1500 Megabytes when loading a four 3D model.")

    def test_memory_usage_3D_one_model(self):
        # Configure parameters to test
        # ----------------------------
        process = psutil.Process(os.getpid())
        self.engine.set_program_view_mode('3D')

        # First model loaded
        # ------------------
        self.remove_all_models()
        model_usage_in_megabytes = self.get_memory_usage_of_load_3d_model(process)
        self.assertLess(model_usage_in_megabytes,
                        550,
                        "Memory usage is not less than 550 Megabytes when loading a 3D model.")

        # Second model loaded
        # ------------------
        self.remove_all_models()
        model_usage_in_megabytes = self.get_memory_usage_of_load_3d_model(process)
        self.assertLess(model_usage_in_megabytes,
                        550,
                        "Memory usage is not less than 550 Megabytes when loading a second 3D model.")

        # Third model loaded
        # ------------------
        self.remove_all_models()
        model_usage_in_megabytes = self.get_memory_usage_of_load_3d_model(process)
        self.assertLess(model_usage_in_megabytes,
                        550,
                        "Memory usage is not less than 550 Megabytes when loading a third 3D model.")

        # Fourth model loaded
        # ------------------
        self.remove_all_models()
        model_usage_in_megabytes = self.get_memory_usage_of_load_3d_model(process)
        self.assertLess(model_usage_in_megabytes,
                        550,
                        "Memory usage is not less than 550 Megabytes when loading a fourth 3D model.")

    def get_memory_usage_of_load_3d_model(self, process):
        """
        Load a 3D model into the program and return the memory used by the operation.

        The memory returned consider all the variables generated of the process, this includes the load of the 2D
        model used to generate the 3D model.
        """
        initial_memory_usage_in_megabytes = self.get_memory_usage_in_megabytes(process)
        self.load_3d_model()
        final_memory_usage_in_megabytes = self.get_memory_usage_in_megabytes(process)
        model_usage_in_megabytes = final_memory_usage_in_megabytes - initial_memory_usage_in_megabytes
        return model_usage_in_megabytes

    def get_memory_usage_in_megabytes(self, process):
        """Get the memory used by the process on megabytes."""
        return process.memory_info().rss >> 20
