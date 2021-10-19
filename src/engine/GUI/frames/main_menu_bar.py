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
Main menu bar frame in the GUI
"""
from typing import TYPE_CHECKING

import OpenGL.GL as GL
import imgui

from src.engine.GUI.frames.frame import Frame
from src.engine.GUI.frames.modal.combine_map_modal import CombineMapModal
from src.engine.GUI.frames.modal.convolve_nan_modal import ConvolveNanModal
from src.engine.GUI.frames.modal.interpolate_nan_map_modal import InterpolateNanMapModal
from src.engine.GUI.frames.modal.subtract_map_modal import SubtractMapModal
from src.engine.scene.map_transformation.fill_nan_map_transformation import FillNanMapTransformation
from src.program.view_mode import ViewMode
from src.utils import get_logger

if TYPE_CHECKING:
    from engine.GUI.guimanager import GUIManager

log = get_logger(module="MAIN_MENU_BAR")


class MainMenuBar(Frame):
    """
    Frame that controls the top menu bar of the application.
    """

    # noinspection PyUnresolvedReferences
    def __init__(self, gui_manager: 'GUIManager'):
        """
        Constructor of the class.

        Args:
            gui_manager: GuiManager of the application.
        """
        super().__init__(gui_manager)

    def __file_menu(self, model_loaded: bool):
        """
        Options that appear on the File option of the main menu bar.

        Args:
            model_loaded: Boolean indicating if there is a model loaded in the program.
        """
        if imgui.begin_menu('File', True):

            # Option to open a NetCDF file
            imgui.menu_item('Open NetCDF file...', 'Ctrl+O', False, True)
            if imgui.is_item_clicked():
                self._GUI_manager.load_netcdf_file_with_dialog()

            # Option to open a CPT file
            imgui.menu_item('Change CPT file...', 'Ctrl+T', False, model_loaded)
            if imgui.is_item_clicked() and model_loaded:
                self._GUI_manager.change_color_file_with_dialog()

            # Option to load a Shapefile file
            imgui.separator()
            imgui.menu_item('Load shapefile file...', 'Ctrl+L', False, model_loaded)
            if imgui.is_item_clicked() and model_loaded:
                log.debug('Clicked load shapefile...')
                self._GUI_manager.load_shapefile_file_with_dialog()

            # Option to export the current model to NetCDF file
            imgui.separator()
            imgui.menu_item('Export current model...', enabled=model_loaded)
            if imgui.is_item_clicked() and model_loaded:
                self._GUI_manager.export_model_as_netcdf(self._GUI_manager.get_active_model_id())
                imgui.close_current_popup()

            imgui.end_menu()

    def __view_menu(self, model_loaded: bool):
        """
        Options that appear on the View option from the main menu bar

        Args:
            model_loaded: Boolean specifying if there is a model loaded in the program.
        """
        if imgui.begin_menu('View'):

            # Option to fix/unfix the frames of the application
            if self._GUI_manager.get_frame_fixed_state():
                imgui.menu_item('Unfix windows positions')
                if imgui.is_item_clicked():
                    self._GUI_manager.fix_frames_position(False)

            else:
                imgui.menu_item('Fix windows positions')
                if imgui.is_item_clicked():
                    self._GUI_manager.fix_frames_position(True)

            # Options to show the points of the map, lines, or to render the model of the map
            imgui.separator()
            imgui.menu_item('Use points', enabled=model_loaded)
            if imgui.is_item_clicked() and model_loaded:
                log.info("Rendering points")
                self._GUI_manager.set_models_polygon_mode(GL.GL_POINT)

            imgui.menu_item('Use wireframes', enabled=model_loaded)
            if imgui.is_item_clicked() and model_loaded:
                log.info("Rendering wireframes")
                self._GUI_manager.set_models_polygon_mode(GL.GL_LINE)

            imgui.menu_item('Fill polygons', enabled=model_loaded)
            if imgui.is_item_clicked() and model_loaded:
                log.info("Rendering filled polygons")
                self._GUI_manager.set_models_polygon_mode(GL.GL_FILL)

            # Option to change to 2D/3D mode. Raise error if the program is in another mode other than 3D or 2D.
            imgui.separator()
            program_view_mode = self._GUI_manager.get_program_view_mode()
            if program_view_mode == ViewMode.mode_3d:
                imgui.menu_item('Change to 2D view', enabled=model_loaded)
                if imgui.is_item_clicked() and model_loaded:
                    self._GUI_manager.set_program_view_mode(ViewMode.mode_2d)

            elif program_view_mode == ViewMode.mode_2d:
                imgui.menu_item('Change to 3D view', enabled=model_loaded)
                if imgui.is_item_clicked() and model_loaded:
                    self._GUI_manager.set_program_view_mode(ViewMode.mode_3d)

            else:
                raise ValueError('That mode is not configured yet.')

            imgui.end_menu()

    def __edit_menu(self, model_loaded: bool):
        """
        Options that appear when opening the Edit option from the main menu bar.

        Args:
            model_loaded: Boolean indicating if there is a model loaded in the program.
        """
        if imgui.begin_menu('Edit', True):

            # Option to undo the last executed action
            imgui.menu_item('Undo', 'CTRL+Z', False, model_loaded)
            if imgui.is_item_clicked() and model_loaded:
                self._GUI_manager.undo_action()
            imgui.end_menu()

    def __map_tools_menu(self, model_loaded: bool):
        """
        Options for the user to modify the maps.

        Args:
            model_loaded: Boolean indicating if there is a model loaded in the program.
        """
        if imgui.begin_menu('Map Tools', True):

            # Get the information ready for the menu to work
            # ----------------------------------------------
            polygon_id_list = self._GUI_manager.get_polygon_id_list()

            polygons_loaded = polygon_id_list != []
            should_execute_logic = model_loaded and polygons_loaded

            # Render the elements of the tools
            # --------------------------------
            imgui.menu_item('Merge maps', None, False, model_loaded)
            if imgui.is_item_clicked() and model_loaded:
                combine_map_modal = CombineMapModal(self._GUI_manager,
                                                    list(self._GUI_manager.get_model_names_dict().keys()),
                                                    list(self._GUI_manager.get_model_names_dict().values()))
                self._GUI_manager.open_modal(combine_map_modal)

            imgui.menu_item('Fill all polygons with NaN', None, False, should_execute_logic)
            if imgui.is_item_clicked() and should_execute_logic:
                map_transformation = FillNanMapTransformation(self._GUI_manager.get_active_model_id())
                self._GUI_manager.apply_map_transformation(map_transformation)

            imgui.menu_item('Interpolate NaN values', None, False, model_loaded)
            if imgui.is_item_clicked() and model_loaded:
                interpolate_nan_map_modal = InterpolateNanMapModal(self._GUI_manager,
                                                                   self._GUI_manager.get_active_model_id())
                self._GUI_manager.open_modal(interpolate_nan_map_modal)

            imgui.menu_item('Eliminate values surrounded by NaN', None, False, model_loaded)
            if imgui.is_item_clicked() and model_loaded:
                self._GUI_manager.open_modal(ConvolveNanModal(self._GUI_manager,
                                                              self._GUI_manager.get_active_model_id()))

            imgui.menu_item('Subtract map heights', None, False, model_loaded)
            if imgui.is_item_clicked() and model_loaded:
                self._GUI_manager.open_modal(SubtractMapModal(self._GUI_manager,
                                                              list(self._GUI_manager.get_model_names_dict().keys()),
                                                              list(self._GUI_manager.get_model_names_dict().values())))

            imgui.end_menu()

    def render(self) -> None:
        """
        Render the main menu bar on the screen.
        Returns: None
        """
        current_model = self._GUI_manager.get_active_model_id()
        model_loaded = current_model is not None

        if imgui.begin_main_menu_bar():
            self.__file_menu(model_loaded)

            self.__edit_menu(model_loaded)

            self.__view_menu(model_loaded)

            self.__map_tools_menu(model_loaded)

            imgui.end_main_menu_bar()
