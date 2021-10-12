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
Module that contains the main class of the program.

Also contains the Enumeration classes for the Tools accepted by the program and the view modes.
"""
import os
import shutil
import time
from typing import TYPE_CHECKING, Union

import easygui

from src.engine.engine import Engine
from src.program.tools import Tools
from src.program.view_mode import ViewMode
from src.utils import get_logger

if TYPE_CHECKING:
    import argparse

log = get_logger(module='PROGRAM')


class Program:
    """
    Class that represents the program and its state.
    """

    # noinspection PyUnresolvedReferences
    def __init__(self, debug_mode: bool = False):
        """
        Constructor of the class.

        Args:
            debug_mode: Boolean indicating if the program should begin in debug mode.
        """
        # PROGRAM VARIABLES
        # -----------------
        self.__engine: Engine = Engine(self,
                                       debug_mode)

        # Default color file to use when loading maps on the application.
        self.__CPT_file: str = os.path.join(os.getcwd(), 'resources', 'colors', 'default.cpt')

        # File to use when making a copy of the loaded model.
        # This copy helps the export process of the models, changing only the height information of the file.
        self.__temp_model_file: str = f'./temp_model_file.{time.time()}.nc'

        # Map 2d variables
        # ----------------
        self.__zoom_level: float = 1
        self.__map_position: list = [0, 0]

        # State variables
        # -----------------------
        self.__active_model: Union[str, None] = None
        self.__active_tool: Union[str, None] = None
        self.__active_polygon: Union[str, None] = None

        self.__view_mode: ViewMode = ViewMode.mode_2d

        self.__loading: bool = False

        self.__debug_mode: bool = debug_mode

    @property
    def engine(self) -> 'Engine':
        """
        Return the engine used by the program to render and control the actions of the user.

        Returns: Engine used by the program.
        """
        return self.__engine

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

    def check_model_temp_file_exists(self) -> bool:
        """
        Check if the temporary file used to store the data of the loaded model on the scene exists.

        Returns: True if the file exists, False otherwise.
        """
        return os.path.exists(self.get_model_temp_file())

    def close(self) -> None:
        """
        Close the program, deleting temporary files and exiting all the resources used on the engine.

        Returns: None
        """
        self.remove_temp_files()
        self.__engine.exit()

    def copy_model_temp_file(self, target_directory: str) -> None:
        """
        Copy the temporary file used to store the model data to the target directory.

        Args:
            target_directory: directory and filename to store the copy of the temporary file.

        Returns: None
        """
        shutil.copy(self.get_model_temp_file(), target_directory)

    def update_model_temp_file(self, reference_file: str) -> None:
        """
        Creates or updates the temporary file used to store the model data.

        The reference file must be a netcdf file with the information of the model that will be used as a temporary
        file.

        This temporary file will be used in the export process of the models, only replacing the height values of the
        file.

        It can be only one temporary file on the program.

        Args:
            reference_file: File to use as the base to the temporary file. Must be a netcdf file.

        Returns: None
        """
        shutil.copy(reference_file, self.get_model_temp_file())

    def get_active_model(self) -> str:
        """
        Get the current model being used by the program.

        Returns: id of the active model
        """
        return self.__active_model

    def get_active_polygon_id(self) -> str:
        """
        Get the id of the active polygon on the program.

        Returns: Id of the active polygon
        """
        return self.__active_polygon

    def get_debug_mode(self) -> bool:
        """
        Returns if the program is in debug mode or not.

        Returns: Boolean indicating if the program is in debug mode or not.
        """
        return self.__debug_mode

    def get_active_tool(self) -> Union[Tools, None]:
        """
        Return the active tool being used in the program.

        Returns: String with the tool being used.
        """
        return self.__active_tool

    def get_cpt_file(self) -> str:
        """
        Get the CTP file currently being used by the program.

        Returns: String with the path to the file.
        """
        return self.__CPT_file

    def get_map_position(self) -> list:
        """
        Get the position of the map in the program.

        Returns: List with the position of the map.
        """
        return self.__map_position

    def get_model_temp_file(self) -> str:
        """
        Get the directory and filename of the file used as temporary to store the model information.

        The temporary file initially stores the same data as the model loaded on the program.

        Returns: String with the directory and filename of the temporary file used for the models.
        """
        return self.__temp_model_file

    def get_view_mode(self) -> ViewMode:
        """
        Get the view mode used by the program.

        Values can be 2D or 3D in string format.

        Returns: view mode being used.
        """
        return self.__view_mode

    def get_zoom_level(self) -> float:
        """
        Get the zoom level currently being used in the program.

        Returns: Zoom level
        """
        return self.__zoom_level

    def is_loading(self) -> bool:
        """
        Returns if the program is loading something or not.

        Returns: Boolean representing if the program is loading.
        """
        return self.__loading

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

    def load_cpt_file_with_dialog(self) -> None:
        """
        Change the CPT file, opening a dialog to select the file to use.

        Returns: None
        """
        path_color_file = self.open_openbox_dialog('Select CPT file...')
        log.debug(f"path_color_file: {path_color_file}")

        self.set_cpt_file(path_color_file)
        self.__engine.update_scene_models_colors()

    def load_netcdf_file_with_dialog(self) -> None:
        """
        Open a dialog to load a new netcdf model into the program.

        Returns: None
        """
        log.info("Open File Dialog")
        path_model = self.open_openbox_dialog('Select NETCDF file...')
        path_color_file = self.get_cpt_file()

        log.debug(f"path_model: {path_model}")
        log.debug(f"path_color_File: {path_color_file}")

        if path_model is not None and path_color_file is not None:
            self.__engine.create_model_from_file(path_color_file, path_model)

    def load_shapefile_file_with_dialog(self) -> None:
        """
        Opens the dialog to select a file and calls the engine to create a new polygon.

        Returns: None
        """
        path_to_shapefile = self.open_openbox_dialog('Select a shapefile file...')

        # noinspection PyMissingOrEmptyDocstring
        def task_in_loading():
            self.__engine.create_polygon_from_file(path_to_shapefile)

        self.__engine.set_task_with_loading_frame(task_in_loading,
                                                  'Loading polygon...')

    # noinspection PyUnresolvedReferences
    def open_file_save_box_dialog(self, message: str, title: str, default_filename: str) -> str:
        """
        Open the file save_box dialog to save new file in the selected directory.

        Args:
            message: Message to show to the user.
            title: Title of the save box.
            default_filename: Default name to use in the file.

        Returns: Path to the selected file. (hard path, not relative)
        """
        file = easygui.filesavebox(message,
                                   title,
                                   default_filename)

        if file is None:
            raise ValueError('Directory not selected')

        return file

    def open_openbox_dialog(self, message) -> str:
        """
        Open a openfile dialog.

        Raise FileNotFound if file is None.

        Args:
            message: Message to show in the openbox.

        Returns: File selected by the user.
        """
        path_to_file = easygui.fileopenbox(message)
        log.debug(f"Path to file: {path_to_file}")

        if path_to_file is None:
            raise FileNotFoundError('File not selected.')

        return path_to_file

    def process_arguments(self, arguments: 'argparse.Namespace') -> None:
        """
        Parse the arguments and do the actions related to each command.

        Args:
            arguments (Namespace):  Arguments received in the command line.

        Returns: None
        """
        if 'model' in arguments and arguments.model is not None:
            log.debug('Loading model from command line  using default color file...')
            self.__engine.create_model_from_file(self.get_cpt_file(), arguments.model)

    def remove_temp_files(self) -> None:
        """
        Remove temporary files generated by the program.

        This method must be called at the end of the program, otherwise it will interfere with the logic of the
        program.

        Returns: None
        """
        if os.path.exists(self.get_model_temp_file()):
            os.remove(self.get_model_temp_file())

    def reset_zoom_level(self) -> None:
        """
        Resets the zoom level to 1

        Returns: None
        """
        self.__zoom_level = 1

    def run(self) -> None:
        """
        Run the program.

        Returns: None
        """
        log.debug('Running program...')
        self.__engine.run()

    def set_active_model(self, new_model_id: Union[str, None]) -> None:
        """
        Set the id of the model used in the application.
        Args:
            new_model_id: ID of the new model to use.

        Returns: None
        """
        self.__active_model = new_model_id

    def set_active_polygon(self, polygon_id: str) -> None:
        """
        Set a new active polygon.

        Args:
            polygon_id: Id of the polygon

        Returns: None
        """
        self.__active_polygon = polygon_id

    def set_active_tool(self, new_tool: Union[Tools, None]) -> None:
        """
        Set the active tool in the program.

        To make the program does not use any tool, use None as the new_tool parameter.

        Args:
            new_tool: New tool being used.

        Returns: None
        """
        if new_tool is not None and type(new_tool) != Tools:
            raise KeyError('Tool value not in the Enum of tools accepted by the program.')

        self.__active_tool = new_tool

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

    def set_loading(self, is_loading: bool) -> None:
        """
        Set if the program is loading or not.

        Args:
            is_loading: Bool to change the loading state.

        Returns: None
        """
        self.__loading = is_loading

    def set_map_position(self, new_position: list) -> None:
        """
        Set the position of the map in the program.

        Args:
            new_position: New position of the map

        Returns: None
        """
        self.__map_position = new_position

    def set_view_mode_2D(self) -> None:
        """
        Set the view mode of the program to 2D.

        Returns: None
        """
        self.__view_mode = ViewMode.mode_2d

    def set_view_mode_3D(self) -> None:
        """
        Set the view mode of the program to 3D.

        Returns: None
        """
        self.__view_mode = ViewMode.mode_3d
