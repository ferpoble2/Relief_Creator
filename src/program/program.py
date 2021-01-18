"""
File that contains the main class of the program.
"""

import os
import easygui
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
        self.__loading = False

        # PROGRAM VARIABLES
        # -----------------
        self.__CPT_file = os.path.join(os.getcwd(), 'input', 'test_colors', 'default.cpt')

        # Map 2d variables
        # ----------------
        self.__zoom_level = 1
        self.__map_position = [0, 0]

        # State variables
        # -----------------------
        self.__active_model = None
        self.__active_tool = None
        self.__active_polygon = None

    def is_loading(self) -> bool:
        """
        Returns if the program is loading something or not.

        Returns: Boolean representing if the program is loading.
        """
        return self.__loading

    def set_loading(self, is_loading: bool) -> None:
        """
        Set if the program is loading or not.

        Args:
            is_loading: Bool to change the loading state.

        Returns: None
        """
        self.__loading = is_loading

    def initialize(self, program: 'Program') -> None:
        """
        Initialize the components of the program.

        Args:
            program: Program to use for the initialization of the components

        Returns:

        """
        log.debug('Initializing program...')
        self.__engine.initialize(self.__engine, program)

    def set_active_model(self, new_model_id: str) -> None:
        """
        Set the id of the model used in the application.
        Args:
            new_model_id: ID of the new model to use.

        Returns:
        """
        self.__active_model = new_model_id

    def set_active_tool(self, new_tool: str) -> None:
        """
        Set the active tool in the program.

        Args:
            new_tool: New tool being used.

        Returns: None
        """
        self.__active_tool = new_tool

    def get_active_model(self) -> str:
        """
        Get the current model being used by the program.

        Returns: id of the active model
        """
        return self.__active_model

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

    def get_active_polygon_id(self) -> str:
        """
        Get the id of the active polygon on the program.

        Returns: Id of the active polygon
        """
        return self.__active_polygon

    def set_active_polygon(self, polygon_id: str) -> None:
        """
        Set a new active polygon.

        Args:
            polygon_id: Id of the polygon

        Returns: None
        """
        self.__active_polygon = polygon_id

    def set_map_position(self, new_position: list) -> None:
        """
        Set the position of the map in the program.

        Args:
            new_position: New position of the map

        Returns: None
        """
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
        if new_file[-4:].lower() != ".cpt":
            raise IOError("File is not a cpt file.")

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
        if self.__zoom_level >= 1:
            self.__zoom_level += 1
        else:
            self.__zoom_level *= 2
        log.debug(f"zoom level: {self.__zoom_level}")

    def less_zoom(self) -> None:
        """
        Reduce on 1 the level of zoom.
        With a minimum of level 0.

        Returns: None
        """
        if self.__zoom_level > 1:
            self.__zoom_level -= 1
        else:
            self.__zoom_level /= 2
        log.debug(f"zoom level: {self.__zoom_level}")

    def load_netcdf_file_with_dialog(self) -> None:
        """
        Open a dialog to load a new netcdf model into the program.

        Returns: None
        """
        log.info("Open File Dialog")
        path_model = easygui.fileopenbox('Select NETCDF file...')
        path_color_file = self.get_cpt_file()

        log.debug(f"path_model: {path_model}")
        log.debug(f"path_color_File: {path_color_file}")

        if path_model is not None and path_color_file is not None:
            self.__engine.refresh_with_model_2d(path_color_file, path_model)

    def change_cpt_file_with_dialog(self) -> None:
        """
        Change the CPT file, opening a dialog to select the file to use.

        Returns: None
        """
        path_color_file = easygui.fileopenbox('Select CPT file...')
        log.debug(f"path_color_file: {path_color_file}")

        self.set_cpt_file(path_color_file)
        self.__engine.update_scene_models_colors()

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
