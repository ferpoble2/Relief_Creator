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

import numpy as np

from src.engine.engine import Engine
from src.input.NetCDF import read_info
from src.program.program import Program


class TestGetModelCoordinates(unittest.TestCase):

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

    def tearDown(self) -> None:
        """
        Delete all temporary files created by the program on the setup or testing processes.

        Returns: None
        """
        self.program.close()

    def test_get_model_coordinates_from_window_coordinates(self):
        self.engine.load_netcdf_file(self.program.get_cpt_file(),
                                     'resources/test_resources/netcdf/test_file_1.nc')

        scene_data = self.engine.get_scene_setting_data()
        begin_scene_x = scene_data['SCENE_BEGIN_X']
        end_scene_x = scene_data['SCENE_BEGIN_X'] + scene_data['SCENE_WIDTH_X']

        begin_scene_y = scene_data['SCENE_BEGIN_Y']
        end_scene_y = scene_data['SCENE_BEGIN_Y'] + scene_data['SCENE_HEIGHT_Y']

        values_array = []
        for x in range(begin_scene_x, end_scene_x, 10):
            for y in range(begin_scene_y, end_scene_y, 10):
                map_coordinates = self.engine.get_map_coordinates_from_window_coordinates(x, y)
                values_array.append(map_coordinates[0])
                values_array.append(map_coordinates[1])

        expected_array = np.load('resources/test_resources/expected_data/npy_data/test_get_coordinates.npy',
                                 allow_pickle=True)
        values_array = np.array(values_array)

        self.assertTrue((expected_array == values_array).all())

    def test_get_model_coordinates_from_window_coordinates_borders(self):
        self.engine.load_netcdf_file(self.program.get_cpt_file(),
                                     'resources/test_resources/netcdf/test_file_1.nc')

        # Get data from the scene
        # -----------------------
        scene_data = self.engine.get_scene_setting_data()
        begin_scene_x = scene_data['SCENE_BEGIN_X']
        end_scene_x = scene_data['SCENE_BEGIN_X'] + scene_data['SCENE_WIDTH_X']

        begin_scene_y = scene_data['SCENE_BEGIN_Y']
        end_scene_y = scene_data['SCENE_BEGIN_Y'] + scene_data['SCENE_HEIGHT_Y']

        # Test the coordinates obtained when asking for points in the the left-middle border
        # ----------------------------------------------------------------------------------
        self.assertEqual((None, None),
                         self.engine.get_map_coordinates_from_window_coordinates(begin_scene_x,
                                                                                 np.average([begin_scene_y,
                                                                                             end_scene_y])))

        self.assertEqual((-179.63451776649745, 9.137055837563466),
                         self.engine.get_map_coordinates_from_window_coordinates(begin_scene_x + 1,
                                                                                 np.average([begin_scene_y,
                                                                                             end_scene_y])))

        # Test the coordinates obtained when asking for points in the the right-middle border
        # ----------------------------------------------------------------------------------
        self.assertEqual((179.63451776649748, 9.137055837563466),
                         self.engine.get_map_coordinates_from_window_coordinates(end_scene_x - 1,
                                                                                 np.average([begin_scene_y,
                                                                                             end_scene_y])))

        self.assertEqual((None, None),
                         self.engine.get_map_coordinates_from_window_coordinates(end_scene_x,
                                                                                 np.average([begin_scene_y,
                                                                                             end_scene_y])))

    def test_get_model_coordinates_from_window_no_model(self):
        scene_data = self.engine.get_scene_setting_data()
        begin_scene_x = scene_data['SCENE_BEGIN_X']
        end_scene_x = scene_data['SCENE_BEGIN_X'] + scene_data['SCENE_WIDTH_X']

        begin_scene_y = scene_data['SCENE_BEGIN_Y']
        end_scene_y = scene_data['SCENE_BEGIN_Y'] + scene_data['SCENE_HEIGHT_Y']

        self.assertEqual((None, None), self.engine.get_map_coordinates_from_window_coordinates(
            np.average([begin_scene_x, end_scene_x]), np.average([begin_scene_y, end_scene_y])))


class TestGetModelHeight(unittest.TestCase):

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

    def tearDown(self) -> None:
        """
        Delete all temporary files created by the program on the setup or testing processes.

        Returns: None
        """
        self.program.close()

    def test_get_model_height_from_coordinates(self):

        # Load model with coordinates separated by 0.1 degrees.
        self.engine.load_netcdf_file(self.program.get_cpt_file(),
                                     'resources/test_resources/netcdf/test_file_1.nc')

        # Get values from the model, step on the for cycle must be lower than 0.1
        values_array = []
        for x in np.arange(-2, 2, 0.01):
            for y in np.arange(-2, 2, 0.01):
                map_height = self.engine.get_map_height_on_coordinates(x, y)
                values_array.append(map_height)

        # np.save('resources/test_resources/expected_data/npy_data/test_get_heights.npy', np.array(values_array))

        # Compare results with the expected data
        expected_array = np.load('resources/test_resources/expected_data/npy_data/test_get_heights.npy')
        values_array = np.array(values_array)

        self.assertTrue((expected_array == values_array).all())

    def test_get_model_height_from_coordinates_on_border(self):
        self.engine.load_netcdf_file(self.program.get_cpt_file(),
                                     'resources/test_resources/netcdf/test_file_1.nc')

        # left border
        self.assertEqual(None, self.engine.get_map_height_on_coordinates(-181, 0))
        self.assertEqual(None, self.engine.get_map_height_on_coordinates(-180, 0))
        self.assertEqual(-5426.098632812505, self.engine.get_map_height_on_coordinates(-179, 0))

        # right border
        self.assertEqual(None, self.engine.get_map_height_on_coordinates(181, 0))
        self.assertEqual(None, self.engine.get_map_height_on_coordinates(180, 0))
        self.assertEqual(-5389.3154296874945, self.engine.get_map_height_on_coordinates(179, 0))

        # top border
        self.assertEqual(None, self.engine.get_map_height_on_coordinates(0, 91))
        self.assertEqual(None, self.engine.get_map_height_on_coordinates(0, 90))
        self.assertEqual(-4252.5439453125, self.engine.get_map_height_on_coordinates(0, 89))

        # bottom border
        self.assertEqual(None, self.engine.get_map_height_on_coordinates(0, -91))
        self.assertEqual(None, self.engine.get_map_height_on_coordinates(0, -90))
        self.assertEqual(2672.0166015625, self.engine.get_map_height_on_coordinates(0, -89))

    def test_get_model_height_no_model(self):
        self.assertEqual(None, self.engine.get_map_height_on_coordinates(0, 0))


class TestModelInformationGetters(unittest.TestCase):

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

    def tearDown(self) -> None:
        """
        Delete all temporary files created by the program on the setup or testing processes.

        Returns: None
        """
        self.program.close()

    def test_get_model_arrays(self):
        self.engine.load_netcdf_file(self.program.get_cpt_file(),
                                     'resources/test_resources/netcdf/test_file_1.nc')

        # read the info of the active model
        x_array, y_array = self.engine.scene.get_active_model_coordinates_arrays()

        # read the info of the file loaded
        x, y, z = read_info('resources/test_resources/netcdf/test_file_1.nc')

        self.assertTrue((np.array(x) == x_array).all())
        self.assertTrue((np.array(y) == y_array).all())

    def test_get_model_arrays_no_model(self):
        self.assertEqual((None, None), self.engine.scene.get_active_model_coordinates_arrays())


if __name__ == '__main__':
    unittest.main()
