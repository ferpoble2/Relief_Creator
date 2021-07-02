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
from src.engine.task_manager import TaskManager


class TestSetTask(unittest.TestCase):

    def test_set_task_do_not_execute(self):
        # Create Task manager and mutable object to store the information within
        tm = TaskManager()
        mutable_object = [None, None]

        # Set the task to execute in future frames

        # noinspection PyMissingOrEmptyDocstring
        def modify_mutable_object(ind, value):
            mutable_object[ind] = value

        tm.set_task(lambda: modify_mutable_object(0, 100), 5)

        # Check that the object has not changed
        self.assertIsNone(mutable_object[0])
        self.assertIsNone(mutable_object[1])

        # Update the manager 4 times, the task should not execute
        tm.update_tasks()
        tm.update_tasks()
        tm.update_tasks()
        tm.update_tasks()

        # Check that the object has not changed
        self.assertIsNone(mutable_object[0])
        self.assertIsNone(mutable_object[1])

    def test_set_task_execute(self):
        # Create Task manager and mutable object to store the information within
        tm = TaskManager()
        mutable_object = [None, None]

        # Set the task to execute in future frames
        # noinspection PyMissingOrEmptyDocstring
        def modify_mutable_object(ind, value):
            mutable_object[ind] = value

        tm.set_task(lambda: modify_mutable_object(0, 100), 1)

        # Check that the object has not changed
        self.assertIsNone(mutable_object[0])
        self.assertIsNone(mutable_object[1])

        # Update the manager to execute the task
        tm.update_tasks()

        # Check that the object has not changed
        self.assertEqual(100, mutable_object[0])
        self.assertIsNone(mutable_object[1])

    def test_error_number_frames(self):
        tm = TaskManager()
        with self.assertRaises(AssertionError):
            tm.set_task(lambda: None, -1)


if __name__ == '__main__':
    unittest.main()
