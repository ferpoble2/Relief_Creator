"""
File that contains the main class of the program.
"""

import os
from src.utils import get_logger

log = get_logger(module='PROGRAM')


class Program:
    """
    Class that represents the program and its state.
    """

    def __init__(self, engine: 'Engine'):
        """
        Constructor of the class.

        Args:
            engine: Engine to use in the program.
        """
        self.__engine = engine

        # PROGRAM VARIABLES
        # -----------------
        self.__CPT_file = os.path.join(os.getcwd(), 'input', 'test_colors', 'default.cpt')
        self.__model_id = None

    def initialize(self, program: 'Program') -> None:
        """
        Initialize the components of the program.

        Args:
            program: Program to use for the initialization of the components

        Returns:

        """
        log.debug('Initializing program...')
        self.__engine.initialize(self.__engine, program)

    def set_model_id(self, new_model_id: str):
        """
        Set the id of the model used in the application.
        Args:
            new_model_id: ID of the new model to use.

        Returns:
        """
        self.__model_id = new_model_id

    def get_cpt_file(self) -> str:
        """
        Get the CTP file currently being used by the program.

        Returns: String with the path to the file.

        """
        return self.__CPT_file

    def set_cpt_file(self, new_file: str) -> None:
        """
        Changes the CPT file used in the program.

        Args:
            new_file: New file to use as a CPT file.

        Returns: None

        """
        self.__CPT_file = new_file

    def run(self) -> None:
        """
        Run the program.

        Returns: None

        """
        log.debug('Running program...')
        self.__engine.run()
