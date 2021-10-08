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
Module with test related to the engine of the program.
"""

import time
import unittest

from src.program.view_mode import ViewMode
from src.utils import dict_to_serializable_dict, json_to_dict
from test.test_case import ProgramTestCase

THREAD_ATTEMPT_TIMES = [0.1, 1, 3, 10, 20, 30, 40, 50, 60]


class TestViewMode(ProgramTestCase):

    def test_default_view_mode(self):
        self.assertEqual(ViewMode.mode_2d,
                         self.program.get_view_mode(),
                         '2D is not the default mode when creating the program.')

    def test_view_mode_3D(self):
        self.engine.set_program_view_mode(ViewMode.mode_3d)
        self.assertEqual(ViewMode.mode_3d,
                         self.program.get_view_mode(),
                         'Mode was not changed to 3D after calling set_program_view_mode')

    def test_view_mode_2D(self):
        self.engine.set_program_view_mode(ViewMode.mode_3d)
        self.engine.set_program_view_mode(ViewMode.mode_2d)
        self.assertEqual(ViewMode.mode_2d,
                         self.program.get_view_mode(),
                         'Mode was not changed to 2D after calling set_program_view_mode')


class TestModelInformation(ProgramTestCase):

    def setUp(self) -> None:
        """
        Load a model into the program.
        """
        super().setUp()
        self.engine.create_model_from_file('resources/test_resources/cpt/colors_0_100_200.cpt',
                                           'resources/test_resources/netcdf/test_file_50_50.nc')

    def test_information_keys(self):
        model_list = self.engine.get_model_list()
        self.assertEqual(1,
                         len(model_list),
                         'Model list does not have only one element.')
        self.assertEqual(
            ['height_array', 'coordinates_array', 'projection_matrix', 'showed_limits', 'shape', 'name'],
            list(self.engine.get_model_information(model_list[0]).keys()),
            'Keys in the dictionary are not equal to the expected keys.'
        )

    def test_information_values(self):
        model_list = self.engine.get_model_list()
        model_information = self.engine.get_model_information(model_list[0])

        model_information_serialized = dict_to_serializable_dict(model_information)
        model_information_expected = json_to_dict('resources/test_resources/expected_data/json_data/model_info.json')

        self.assertEqual(model_information_serialized,
                         model_information_expected,
                         'Model information generated is not equal to the expected.')


class TestSetActiveModel(ProgramTestCase):

    def test_set_active_model(self):
        self.assertIsNone(self.engine.get_active_model_id(),
                          "Active model is not None when there is no model.")

        self.engine.create_model_from_file('resources/test_resources/cpt/colors_0_100_200.cpt',
                                           'resources/test_resources/netcdf/test_file_50_50.nc')
        self.engine.create_model_from_file('resources/test_resources/cpt/colors_0_100_200.cpt',
                                           'resources/test_resources/netcdf/test_file_50_50.nc')
        self.assertEqual('1',
                         self.engine.get_active_model_id(),
                         "Active model id is not 1 after loading 2 models into the engine.")

        self.engine.set_active_model('0')
        self.assertEqual('0',
                         self.engine.get_active_model_id(),
                         "Active model was not changed to 0")

    def test_set_active_model_to_None(self):
        self.assertIsNone(self.engine.get_active_model_id(),
                          "Active model is not None when there is no model.")

        self.engine.create_model_from_file('resources/test_resources/cpt/colors_0_100_200.cpt',
                                           'resources/test_resources/netcdf/test_file_50_50.nc')
        self.assertEqual('0',
                         self.engine.get_active_model_id(),
                         "Active model id is not 0 after loading a model into the engine.")

        self.engine.set_active_model(None)
        self.assertIsNone(self.engine.get_active_model_id(),
                          "Model was not changed to None.")


class TestSetThreadTask(ProgramTestCase):

    def test_set_thread_task(self):
        self.engine.use_threads = True

        for task_sleep_time in THREAD_ATTEMPT_TIMES:

            try:
                # Check if the task is iin fact executed in a new thread
                initial_time = time.time()
                self.engine.set_thread_task(lambda: time.sleep(task_sleep_time), lambda: None)
                final_time = time.time()

                # Check that the sleep logic is executing in another thread
                self.assertTrue(final_time - initial_time < task_sleep_time / 2)

                # Wait for the thread to end
                time.sleep(task_sleep_time)

            # Continue if there is more values to try, raise the exception if there is no more values.
            except AssertionError as e:
                if task_sleep_time == THREAD_ATTEMPT_TIMES[-1]:
                    raise e
                else:
                    continue

            else:
                break

    def test_set_thread_task_return_value(self):
        self.engine.use_threads = True

        def sleep_then_return_50(time_to_sleep):
            """Function that sleep and then return the integer 50."""
            time.sleep(time_to_sleep)
            return 50

        return_value = []
        for task_sleep_time in THREAD_ATTEMPT_TIMES:

            try:
                # Check if the task is iin fact executed in a new thread
                initial_time = time.time()
                self.engine.set_thread_task(lambda: sleep_then_return_50(task_sleep_time),
                                            lambda x: return_value.insert(0, x))
                final_time = time.time()

                # Check that the sleep logic is executing in another thread
                self.assertTrue(final_time - initial_time < task_sleep_time / 2)

                # Wait for the thread to end
                time.sleep(task_sleep_time)
                self.engine.run(1, False)
                self.assertEqual(return_value[0],
                                 50,
                                 "Returned value from the thread was not stored in the list.")

            # Continue if there is more values to try, raise the exception if there is no more values.
            except (AssertionError, IndexError) as e:
                if task_sleep_time == THREAD_ATTEMPT_TIMES[-1]:
                    raise e
                else:
                    continue

            else:
                break


if __name__ == '__main__':
    unittest.main()
