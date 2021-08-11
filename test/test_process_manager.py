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
File wth logic that test the process manager of the application.

Due to python implementations, all functions passed to the parallel process must be defined public. They can not
be private, protected, or local to a function or class.
"""

import unittest
import time
import queue

from src.engine.process_manager import ProcessManager

# Variables and functions used in testing.
TEST_MUTABLE_OBJECT = [None, None, None]
PROCESS_CREATION_TIME = 5  # time in seconds to wait for a process to create
PROCESS_CREATION_TIMES = [0, 1, 5, 10, 20, 30]  # time in seconds to wait for the process to create


def do_nothing_function():
    """Do nothing and return nothing"""
    return


def return_value_plus_50(value):
    """Return the value plus 50."""
    return value + 50


def change_mutable_object(value, ind, mutable_object):
    """Change the value of the mutable object defined at the beginning of the test."""
    mutable_object[ind] = value


def change_global_mutable_object(value, ind):
    """Change the value of the mutable object defined at the beginning of the test."""
    TEST_MUTABLE_OBJECT[ind] = value


class TestProcessTask(unittest.TestCase):

    def test_code_in_another_process(self):
        pm = ProcessManager()

        initial_time = time.time()
        pm.create_parallel_process(time.sleep, [PROCESS_CREATION_TIME * 2])
        final_time = time.time()

        # Check that the sleep logic is executing in another thread
        self.assertTrue(final_time - initial_time < PROCESS_CREATION_TIME)

        # Wait for the process to end
        time.sleep(5)

    def test_execution_then_task(self):

        # Execute a parallel process that does nothing and then execute a function that changes the mutable object
        # values. The parallel process return None, and thus, a new argument should not be added to the then function.
        for process_creation_time in PROCESS_CREATION_TIMES:
            pm = ProcessManager()
            pm.create_parallel_process(parallel_task=do_nothing_function,
                                       parallel_task_args=None,
                                       then_function=change_mutable_object,
                                       then_function_args=[50, 0, TEST_MUTABLE_OBJECT])
            time.sleep(process_creation_time)
            pm.update_process()

            # Check values
            try:
                self.assertEqual(50, TEST_MUTABLE_OBJECT[0])
                self.assertEqual(None, TEST_MUTABLE_OBJECT[1])
                break

            except AssertionError as e:
                if process_creation_time == PROCESS_CREATION_TIMES[-1]:
                    raise e

        # Return values to normal
        TEST_MUTABLE_OBJECT[0] = None

    def test_execution_then_task_modify_global_object(self):
        pm = ProcessManager()

        # Execute thread and wait for it to end.

        # Execute a parallel process that does nothing and then execute a function that changes the mutable object
        # values. The parallel process return None, and thus, a new argument should not be added to the then function.
        pm.create_parallel_process(parallel_task=do_nothing_function,
                                   parallel_task_args=None,
                                   then_function=change_global_mutable_object,
                                   then_function_args=[50, 0])
        time.sleep(PROCESS_CREATION_TIME)

        # Update thread task to execute the then logic
        pm.update_process()

        # Check values
        self.assertEqual(50, TEST_MUTABLE_OBJECT[0])
        self.assertEqual(None, TEST_MUTABLE_OBJECT[1])

        # Return values of object to normal
        TEST_MUTABLE_OBJECT[0] = None

    def test_thread_execution_with_return_argument(self):
        pm = ProcessManager()

        # Execute thread and wait for it to end

        # The parallel task is executed in another process, and thus, all the variables modified on the other process
        # will not update their values in the main process. The Then function can receive the return argument from the
        # parallel process task as the first argument, being able to modify the corresponding variables on the main
        # process with the information calculated on the parallel process.
        pm.create_parallel_process(return_value_plus_50,
                                   [100],
                                   change_mutable_object,
                                   [1, TEST_MUTABLE_OBJECT])
        time.sleep(PROCESS_CREATION_TIME)

        # Update thread task to execute the then logic
        pm.update_process()

        # Check values
        self.assertEqual(150, TEST_MUTABLE_OBJECT[1])
        self.assertEqual(None, TEST_MUTABLE_OBJECT[0])

        # Return values to normal
        TEST_MUTABLE_OBJECT[1] = None

    def test_real_parallel_task_execution(self):
        pm = ProcessManager()

        q = queue.Queue()
        pm.true_parallel_task(q, lambda a, b: a + b, 15, 30)

        self.assertEqual([45], list(q.queue))


if __name__ == '__main__':
    unittest.main()
