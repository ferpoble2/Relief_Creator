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
File with the definition of the TaskManager class. Class in charge of the tasks on the program.

Tasks are code or logic that will be executed after the indicated number of frames. This logic is not executed
in another thread or process. To execute another thread check the ThreadManager class and for another process
check the ProcessManager class.
"""


class TaskManager:
    """
    Class in charge of the management of the tasks on the engine.

    Tasks are functions that will be executed after a specified number of frames happened on the application. This logic
    is not executed in another thread or process. To execute another thread check the ThreadManager class and for
    another process check the ProcessManager class.
    """

    def __init__(self):
        """
        Constructor of the class.
        """
        self.__pending_task_list = []

    def set_task(self, task: callable, n_frames: int = 2) -> None:
        """
        Add a new task to the list of tasks to be executed.

        Args:
            task: Function with no arguments with the logic to execute.
            n_frames: Number of frames to wait for the execution of the function.

        Returns: None
        """
        self.__pending_task_list.append({
            'task': task,
            'frames': n_frames  # need to be 2 to really wait one full frame
        })

    def update_tasks(self) -> None:
        """
        Method that must be called on each frame of the application.

        This method updates the variables that count the frames of the active tasks that are present in the program
        in a given time.

        Returns: None
        """
        to_delete = []

        # check on the tasks
        for task in self.__pending_task_list:

            # Subtract one frame from the task
            task['frames'] -= 1

            # execute it if frames to wait is zero
            if task['frames'] == 0:
                task['task']()
                to_delete.append(task)

        # delete tasks already executed
        for task in to_delete:
            self.__pending_task_list.remove(task)
