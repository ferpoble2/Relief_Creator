# BEGIN GPL LICENSE BLOCK
#
#     This program is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# END GPL LICENSE BLOCK

"""
File with the class ThreadManager, class in charge of the management of the threads in the engine.

Threads must be update regularly so the function programmed as then should be called. Otherwise, even if the logic
programmed in the thread ends, the then function will not be called.
"""
from threading import Thread


class ThreadManager:
    """
    Class in charge of the management of the threads on the program.
    """

    def __init__(self):
        """
        Constructor of the class.
        """
        self.__threads_list = []

    def update_threads(self):
        """
        Method that update the finished threads and calls the then_task associated to the threads.

        If the threads ended their execution, then the then_function is called, if they did not end their execution,
        then this method does nothing.
        """
        to_delete = []
        for thread_pair in self.__threads_list:
            if not thread_pair['thread'].is_alive():
                to_delete.append(thread_pair)

                # check if the return object is None or not to give it to the then task
                if thread_pair['return_array'][0] is not None:
                    thread_pair['then_func'](thread_pair['return_array'][0], *thread_pair['then_args'])
                else:
                    thread_pair['then_func'](*thread_pair['then_args'])

        for thread_ended in to_delete:
            self.__threads_list.remove(thread_ended)

    def set_thread_task(self, parallel_task, then, parallel_task_args=None, then_task_args=None) -> None:
        """
        Add and start a new thread with the current task. At the end of the thread, the then
        function is called.

        If the parallel task return something other than none, then the return object is added
        as the first parameter of the then function when called.

        Args:
            then_task_args: List of argument to use in the then task
            parallel_task_args: List of argument to use in the parallel task
            parallel_task: Task to be executed in parallel
            then: Task to be executed in the main thread after the parallel task

        Returns: None
        """
        # Create and start the thread
        if then_task_args is None:
            then_task_args = []
        if parallel_task_args is None:
            parallel_task_args = []

        # Define a mutable object where to store the return value of the parallel task.
        return_value_list = [None]

        # Define a external function to act as a decorator for the parallel task given.
        # noinspection PyMissingOrEmptyDocstring,PyShadowingNames
        def parallel_routine(return_value_list, parallel_task, arg_list):
            return_value = parallel_task(*arg_list)
            return_value_list[0] = return_value

        # Create a thread with the external function.
        thread = Thread(target=parallel_routine, args=(return_value_list, parallel_task, parallel_task_args))
        thread.start()

        # Add thread to the list
        self.__threads_list.append(
            {'thread': thread,
             'return_array': return_value_list,
             'then_func': then,
             'then_args': then_task_args}
        )
