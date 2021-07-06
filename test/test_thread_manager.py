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
import time

from src.engine.thread_manager import ThreadManager


class TestThreadTask(unittest.TestCase):

    def test_code_in_another_thread(self):
        tm = ThreadManager()

        # In case that the task fails due to execution time errors (CPU too loaded, disk problems, etc...) try
        # different values to tests the execution of the threads.
        attempt_sleep_values = [0.1, 1, 3, 10, 20, 30]
        for task_sleep_time in attempt_sleep_values:

            try:
                # Check if the task is iin fact executed in a new thread
                initial_time = time.time()
                tm.set_thread_task(lambda: time.sleep(task_sleep_time), lambda: None)
                final_time = time.time()

                # Check that the sleep logic is executing in another thread
                self.assertTrue(final_time - initial_time < task_sleep_time / 2)

                # Wait for the thread to end
                time.sleep(task_sleep_time)

            # Continue if there is more values to try, raise the exception if there is no more values.
            except AssertionError as e:
                if task_sleep_time == attempt_sleep_values[-1]:
                    raise e
                else:
                    continue

            else:
                break

    def test_execution_then_task(self):
        tm = ThreadManager()
        mutable_object = [None, None, None]

        # noinspection PyMissingOrEmptyDocstring
        def change_mutable_object_value(index, value):
            mutable_object[index] = value

        # Execute thread and wait for it to end
        tm.set_thread_task(lambda: change_mutable_object_value(0, 50), lambda: change_mutable_object_value(1, 100))

        # In case that the task fails due to execution time errors (CPU too loaded, disk problems, etc...) try
        # different values to tests the execution of the threads.
        attempt_sleep_values = [0.1, 1, 3, 10, 20, 30]
        for task_sleep_time in attempt_sleep_values:

            try:
                time.sleep(task_sleep_time)

                # Update thread task to execute the then logic
                tm.update_threads()

                # Check values
                self.assertEqual(50, mutable_object[0])
                self.assertEqual(100, mutable_object[1])

            # Continue if there is more values to try, raise exception if there is no more values.
            except AssertionError as e:
                if task_sleep_time == attempt_sleep_values[-1]:
                    raise e
                else:
                    continue

            else:
                break

    def test_thread_execution_with_return_argument(self):
        tm = ThreadManager()
        mutable_object = [None, None, None]

        # noinspection PyMissingOrEmptyDocstring
        def change_mutable_object_value(index, value):
            mutable_object[index] = value
            return value

        # Execute thread and wait for it to end
        tm.set_thread_task(lambda: change_mutable_object_value(0, 50),
                           lambda value: change_mutable_object_value(1, value + 20))

        # In case that the task fails due to execution time errors (CPU too loaded, disk problems, etc...) try
        # different values to tests the execution of the threads.
        attempt_sleep_values = [0.1, 1, 3, 10, 20, 30]
        for task_sleep_time in attempt_sleep_values:

            try:
                time.sleep(task_sleep_time)

                # Update thread task to execute the then logic
                tm.update_threads()

                # Check values
                self.assertEqual(50, mutable_object[0])
                self.assertEqual(70, mutable_object[1])

            # Continue if there is more values to try, raise exception if there is no more values.
            except AssertionError as e:
                if task_sleep_time == attempt_sleep_values[-1]:
                    raise e
                else:
                    continue

            else:
                break


if __name__ == '__main__':
    unittest.main()
