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
File with the definition of the ProcessManager class, class in charge of the management of the process raised by the
engine.

Parallel process are executed in another space of memory than the main process, and thus, they need to copy all the
variables and data from the main process to the new process. This can make process slower than threads or task, since
the last two does not need to copy the variables and data to another space of memory.

All the methods called on the process must be parsed and copied to the new space of memory, and thus, all the functions
used for the parallel process must be public (they can not be private, protected, local to a class or functions or
lambda).
"""

from multiprocessing import Process, Queue
import queue


class ProcessManager:
    """
    Class in charge of the management of the process.

    All the methods called on the process must be parsed and copied to the new space of memory, and thus, all the
    functions used for the parallel process must be public (they can not be private, protected, local to a class or
    functions or lambda).

    WARNING: The use of this module can be slow since it has to copy all the variables to another memory to
    execute the new process. (use threads if this step is too slow)
    """

    def __init__(self):
        """
        Constructor of the class.
        """
        self.__process_list = []

    def true_parallel_task(self, q, function, *args) -> None:
        """
        Function to really use as the parallel process.

        This function should be private but due to a bug in the multiprocessing module it has to be public.

        Args:
            q: Queue to use for communicating.
            function: Task to use.
            *args: Args to use in the function.

        Returns: Queue used with the return value included.
        """
        ret = function(*args)
        q.put(ret)
        return q

    def create_parallel_process(self, parallel_task: callable,
                                parallel_task_args=None,
                                then_function: callable = lambda: None,
                                then_function_args=None) -> None:
        """
        Create a new process and start it.

        If the return parameter of the parallel_task is not none, then the returned value will be used as first
        argument of the then_function.

        Args:
            parallel_task: Function to execute in a new process.
            parallel_task_args: Arguments to pass to the parallel task.
            then_function: Task to execute after the process ends.
            then_function_args: Arguments to pass to the task that is executed after the process.

        Returns: None
        """

        if then_function_args is None:
            then_function_args = []
        if parallel_task_args is None:
            parallel_task_args = []

        q = Queue()
        p = Process(target=self.true_parallel_task, args=(q, parallel_task) + tuple(parallel_task_args))
        p.start()

        self.__process_list.append({
            'process': p,
            'queue': q,
            'then_function': then_function,
            'then_function_args': then_function_args
        })

    def update_process(self) -> None:
        """
        Update the process, calling the then_task if they already finished.

        Returns: None
        """
        to_delete = []
        for process in self.__process_list:

            try:
                ret = process['queue'].get(False)
                process['process'].join()

                # Execute the then function with the returned argument only if the return value of the
                # parallel process is not None.
                if ret is not None:
                    process['then_function'](ret, *process['then_function_args'])
                else:
                    process['then_function'](*process['then_function_args'])

                # Add the process as one to delete.
                to_delete.append(process)

            except queue.Empty:
                pass

        for process in to_delete:
            self.__process_list.remove(process)
