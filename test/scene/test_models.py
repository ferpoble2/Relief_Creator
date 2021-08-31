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

import unittest
import warnings

from engine.engine import Engine
from program.program import Program

COLOR_FILE_LOCATION = 'resources/test_resources/cpt/colors_0_100_200.cpt'
PATH_TO_MODEL_1 = 'resources/test_resources/netcdf/test_file_1.nc'
PATH_TO_MODEL_2 = 'resources/test_resources/netcdf/test_file_2.nc'
PATH_TO_MODEL_3 = 'resources/test_resources/netcdf/test_file_3.nc'
PATH_TO_MODEL_4 = 'resources/test_resources/netcdf/test_file_4.nc'


class TestLoadedModelsList(unittest.TestCase):

    def test_model_list(self):
        """
        Test the list of models on the program.

        The program must only have one active model at the same time. The list of models should not be longer than
        one element. If that is not the case anymore, then mark this test as one who should fail.
        """
        warnings.simplefilter("ignore", ResourceWarning)

        engine = Engine()
        engine.should_use_threads(False)

        self.assertEqual(engine.get_model_list(), [], 'List of models is not empty.')

        engine.load_netcdf_file(COLOR_FILE_LOCATION, PATH_TO_MODEL_1)
        self.assertEqual(engine.get_model_list(), [0], 'First models should be assigned to the ID 0.')

        engine.load_netcdf_file(COLOR_FILE_LOCATION, PATH_TO_MODEL_2)
        engine.load_netcdf_file(COLOR_FILE_LOCATION, PATH_TO_MODEL_3)
        engine.load_netcdf_file(COLOR_FILE_LOCATION, PATH_TO_MODEL_4)
        self.assertEqual(engine.get_model_list(), [3], 'The fourth models is not assigned to the ID 3.')


if __name__ == '__main__':
    unittest.main()
