"""
File with the definition of the ProcessManager class, class in charge of the management of the process raised by the
engine.
"""

from multiprocessing import Process, Queue
import queue


class ProcessManager:
    """
    Class in charge of the management of the process.
    """

    def __init__(self):
        """
        Constructor of the class.
        """
        self.__process_list = []

    def true_parallel_task(self, q, function, *args) -> None:
        """
        Function to really use as the parallel process.

        Args:
            q: Queue to use for communicating.
            function: Task to use.
            *args: Args to use in the function.

        Returns: None
        """
        ret = function(*args)
        q.put(ret)

    def create_parallel_process(self, parallel_task: callable, parallel_task_args: list, then_function: callable,
                                then_function_args: list) -> None:
        """
        Create a new process and start it.

        If the return parameter of the parallel task is not none, then the first parameter of the then_task will be
        the returned parameter.

        Args:
            parallel_task: Function to execute in a new process.
            parallel_task_args: Arguments to pass to the parallel task.
            then_function: Task to execute after the process ends.
            then_function_args: Arguments to pass to the task that is executed after the process.

        Returns: None
        """

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
                process['then_function'](ret, *process['then_function_args'])
                to_delete.append(process)
            except queue.Empty:
                pass

        for process in to_delete:
            self.__process_list.remove(process)


if __name__ == '__main__':

    import time

    # move outside to run this code.

    # noinspection PyMissingOrEmptyDocstring
    def parallel_one(something):
        print('to sleep')
        time.sleep(2.5)
        print(something)
        return 300

    # noinspection PyMissingOrEmptyDocstring
    def then_task(number, another_number):
        print(number)
        print(another_number)


    pm = ProcessManager()

    pm.create_parallel_process(parallel_one, ['something'], then_task, [90000])
    while True:
        pm.update_process()
