"""
File with the class ThreadManager, class in charge of the management of the threads in the engine.
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
        """
        to_delete = []
        for thread_pair in self.__threads_list:
            if not thread_pair['thread'].is_alive():
                to_delete.append(thread_pair)
                thread_pair['then_func'](*thread_pair['then_args'])

        for thread_ended in to_delete:
            self.__threads_list.remove(thread_ended)

    def set_thread_task(self, parallel_task, then, parallel_task_args=None, then_task_args=None) -> None:
        """
        Add and start a new thread with the current task. At the end of the thread, the then
        function is called.

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

        thread = Thread(target=parallel_task, args=parallel_task_args)
        thread.start()

        # Add thread to the list
        self.__threads_list.append(
            {'thread': thread,
             'then_func': then,
             'then_args': then_task_args}
        )
