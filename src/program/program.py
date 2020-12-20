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
        self.__zoom_level = 1
        self.__map_position = [0, 0]
        self.__active_tool = None

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

    def set_active_tool(self, new_tool: str) -> None:
        """
        Set the active tool in the program.

        Args:
            new_tool: New tool being used.

        Returns: None
        """
        self.__active_tool = new_tool

    def get_active_tool(self) -> str:
        """
        Return the active tool being used in the program.

        Returns: String with the tool being used.
        """
        return self.__active_tool

    def get_map_position(self) -> list:
        """
        Get the position of the map in the program.

        Returns: List with the position of the map.
        """
        return self.__map_position

    def set_map_position(self, new_position: list) -> None:
        self.__map_position = new_position

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

    def reset_zoom_level(self) -> None:
        """
        Resets the zoom level to 1

        Returns: None
        """
        self.__zoom_level = 1

    def add_zoom(self) -> None:
        """
        Increase on 1 the level of zoom.

        Returns: None
        """
        self.__zoom_level += 1
        log.debug(f"zoom level: {self.__zoom_level}")

    def less_zoom(self) -> None:
        """
        Reduce on 1 the level of zoom.
        With a minimum of level 0.

        Returns: None
        """
        if self.__zoom_level > 1:
            self.__zoom_level -= 1

        log.debug(f"zoom level: {self.__zoom_level}")

    def get_zoom_level(self) -> float:
        """
        Get the zoom level currently being used in the program.

        Returns: Zoom level
        """
        return self.__zoom_level

    def run(self) -> None:
        """
        Run the program.

        Returns: None

        """
        log.debug('Running program...')
        self.__engine.run()
