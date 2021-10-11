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

import numpy as np

from src.error.scene_error import SceneError
from src.input.NetCDF import read_info
from test.test_case import ProgramTestCase

COLOR_FILE_LOCATION = 'resources/test_resources/cpt/colors_0_100_200.cpt'
PATH_TO_MODEL_1 = 'resources/test_resources/netcdf/test_file_1.nc'
PATH_TO_MODEL_2 = 'resources/test_resources/netcdf/test_file_3.nc'


class TestGetModelCoordinates(ProgramTestCase):

    def test_get_model_coordinates_from_window_coordinates(self):
        self.engine.create_model_from_file(self.program.get_cpt_file(),
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
        self.engine.create_model_from_file(self.program.get_cpt_file(),
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


class TestGetModelHeight(ProgramTestCase):

    def test_get_model_height_from_coordinates(self):

        # Load model with coordinates separated by 0.1 degrees.
        self.engine.create_model_from_file(self.program.get_cpt_file(),
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
        self.engine.create_model_from_file(self.program.get_cpt_file(),
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


class TestModelInformationGetters(ProgramTestCase):

    def test_get_model_arrays(self):
        self.engine.create_model_from_file(self.program.get_cpt_file(),
                                           'resources/test_resources/netcdf/test_file_1.nc')

        # read the info of the active model
        x_array, y_array = self.engine.scene.get_model_coordinates_arrays(self.program.get_active_model())

        # read the info of the file loaded
        x, y, z = read_info('resources/test_resources/netcdf/test_file_1.nc')

        self.assertTrue((np.array(x) == x_array).all())
        self.assertTrue((np.array(y) == y_array).all())

    def test_get_model_arrays_no_model(self):
        self.assertEqual((None, None), self.engine.scene.get_model_coordinates_arrays(self.program.get_active_model()))


class TestGetMaxMinHeights(ProgramTestCase):

    def test_get_max_min(self):
        scene = self.engine.scene

        self.engine.create_model_from_file('resources/test_resources/cpt/colors_0_100_200.cpt',
                                           'resources/test_resources/netcdf/test_file_50_50.nc')
        polygon_id = self.__create_and_initialize_polygon(self.engine)
        results = scene.calculate_max_min_height(self.engine.get_active_model_id(),
                                                 polygon_id)
        self.assertEqual((38, 22),
                         results,
                         "The maximum and minimum heights are not equal to the expected.")

    def test_polygon_not_enough_points(self):
        scene = self.engine.scene

        self.engine.create_model_from_file('resources/test_resources/cpt/colors_0_100_200.cpt',
                                           'resources/test_resources/netcdf/test_file_50_50.nc')
        polygon_id = self.engine.create_new_polygon()

        with self.assertRaises(SceneError) as context:
            scene.calculate_max_min_height(self.engine.get_active_model_id(),
                                           polygon_id)

        self.assertIsInstance(context.exception, SceneError, "Exception raised is not of the class SceneError")
        self.assertEqual(2,
                         context.exception.code,
                         "The code of the exception is not the one expected.")

    def test_polygon_not_planar(self):
        scene = self.engine.scene

        self.engine.create_model_from_file('resources/test_resources/cpt/colors_0_100_200.cpt',
                                           'resources/test_resources/netcdf/test_file_50_50.nc')
        polygon_id = self.__create_and_initialize_non_planar_polygon(self.engine)

        with self.assertRaises(SceneError) as context:
            scene.calculate_max_min_height(self.engine.get_active_model_id(),
                                           polygon_id)

        self.assertIsInstance(context.exception, SceneError, "Exception raised is not of the class SceneError")
        self.assertEqual(1,
                         context.exception.code,
                         "The code of the exception is not the one expected.")

    def __create_and_initialize_non_planar_polygon(self, engine):
        """
        Create a non planar polygon on the engine and initialize it with four points.

        Add the following points:
            (10,10)
            (10,20)
            (20,10)
            (20,20)

        Args:
            engine: Engine to use for the creation of the polygon.

        Returns: The ID of the generated polygon.
        """
        polygon_id = engine.create_new_polygon()
        engine.set_active_polygon(polygon_id)
        engine.add_new_vertex_to_active_polygon_using_real_coords(10, 10)
        engine.add_new_vertex_to_active_polygon_using_real_coords(10, 20)
        engine.add_new_vertex_to_active_polygon_using_real_coords(20, 10)
        engine.add_new_vertex_to_active_polygon_using_real_coords(20, 20)
        return polygon_id

    def __create_and_initialize_polygon(self, engine):
        """
        Create a polygon on the engine and initialize it with four points.

        Add the following points:
            (10,10)
            (10,20)
            (20,20)
            (20,10)

        Args:
            engine: Engine to use for the creation of the polygon.

        Returns: The ID of the generated polygon.
        """
        polygon_id = engine.create_new_polygon()
        engine.set_active_polygon(polygon_id)
        engine.add_new_vertex_to_active_polygon_using_real_coords(10, 10)
        engine.add_new_vertex_to_active_polygon_using_real_coords(10, 20)
        engine.add_new_vertex_to_active_polygon_using_real_coords(20, 20)
        engine.add_new_vertex_to_active_polygon_using_real_coords(20, 10)
        return polygon_id


class TestLoadedModelsList(ProgramTestCase):

    def test_3d_model_list(self):
        self.program.set_view_mode_3D()

        self.assertEqual([], self.engine.get_3d_model_list(), 'List of models is not empty.')

        self.engine.create_model_from_file(COLOR_FILE_LOCATION, PATH_TO_MODEL_1)
        self.engine.run(10, False)
        self.assertEqual(['0'], self.engine.get_3d_model_list(), 'First models should be assigned to the ID 0.')

        self.engine.create_model_from_file(COLOR_FILE_LOCATION, PATH_TO_MODEL_1)
        self.engine.run(5, False)
        self.engine.create_model_from_file(COLOR_FILE_LOCATION, PATH_TO_MODEL_1)
        self.engine.run(5, False)
        self.engine.create_model_from_file(COLOR_FILE_LOCATION, PATH_TO_MODEL_1)
        self.engine.run(5, False)
        self.assertEqual(['3'], self.engine.get_3d_model_list(),
                         'The fourth models is not assigned to the ID 3.')

    def test_model_list(self):
        self.assertEqual([], self.engine.get_model_list(), 'List of models is not empty.')

        self.engine.create_model_from_file(COLOR_FILE_LOCATION, PATH_TO_MODEL_2)
        self.assertEqual(['0'], self.engine.get_model_list(), 'First models should be assigned to the ID 0.')

        self.engine.create_model_from_file(COLOR_FILE_LOCATION, PATH_TO_MODEL_2)
        self.engine.create_model_from_file(COLOR_FILE_LOCATION, PATH_TO_MODEL_2)
        self.engine.create_model_from_file(COLOR_FILE_LOCATION, PATH_TO_MODEL_2)
        self.assertEqual(['0', '1', '2', '3'], self.engine.get_model_list(),
                         'The fourth models is not assigned to the ID 3.')


if __name__ == '__main__':
    unittest.main()
