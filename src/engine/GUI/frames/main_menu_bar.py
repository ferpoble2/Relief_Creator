"""
Main menu bar frame in the GUI
"""
from src.engine.GUI.frames.frame import Frame
from src.utils import get_logger

import imgui
import shapefile
import OpenGL.GL as GL

log = get_logger(module="MAIN_MENU_BAR")


class MainMenuBar(Frame):
    """
    Frame that controls the top menu bar of the application.
    """

    def __init__(self, gui_manager: 'GUIManager'):
        """
        Constructor of the class.

        Args:
            gui_manager: GuiManager of the application.
        """
        super().__init__(gui_manager)

    def render(self) -> None:
        """
        Render the main menu bar on the screen.
        Returns: None
        """

        if imgui.begin_main_menu_bar():
            # first menu dropdown
            self.__file_menu()

            # second menu dropdown
            self.__edit_menu()

            # third menu dropdown
            self.__view_menu()

            imgui.end_main_menu_bar()

    def __file_menu(self):
        """
        Options that appear on the File option of the main menu bar.
        """
        if imgui.begin_menu('File', True):
            imgui.menu_item('Open NetCDF file...', 'Ctrl+O', False, True)
            if imgui.is_item_clicked():
                self._GUI_manager.load_netcdf_file_with_dialog()

            imgui.menu_item('Change CPT file...', 'Ctrl+T', False, True)
            if imgui.is_item_clicked():
                self._GUI_manager.change_color_file_with_dialog()

            imgui.separator()
            imgui.menu_item('Load shapefile file...', 'Ctrl+L', False, True)
            if imgui.is_item_clicked():
                log.debug('Clicked load shapefile...')
                self._GUI_manager.load_shapefile_file_with_dialog()

            imgui.separator()
            imgui.menu_item('Export current model...')
            if imgui.is_item_clicked():
                try:
                    self._GUI_manager.export_model_as_netcdf(self._GUI_manager.get_active_model_id())
                    self._GUI_manager.set_modal_text('Information', 'Model exported successfully')
                    imgui.close_current_popup()
                except TypeError:
                    self._GUI_manager.set_modal_text('Error', 'This model can not be exported.')
                except ValueError:
                    self._GUI_manager.set_modal_text('Error', 'You must select a directory to save the model.')

            imgui.end_menu()

    def __view_menu(self):
        """
        Options that appear on the View option from the main menu bar
        """
        if imgui.begin_menu('View'):

            if self._GUI_manager.are_frame_fixed():
                imgui.menu_item('Unfix Windows Positions')
                if imgui.is_item_clicked():
                    self._GUI_manager.fix_frames_position(False)

            else:
                imgui.menu_item('Fix Windows Positions')
                if imgui.is_item_clicked():
                    self._GUI_manager.fix_frames_position(True)

            imgui.separator()

            imgui.menu_item('Use points')
            if imgui.is_item_clicked():
                log.info("Rendering points")
                self._GUI_manager.set_models_polygon_mode(GL.GL_POINT)

            imgui.menu_item('Use wireframes')
            if imgui.is_item_clicked():
                log.info("Rendering wireframes")
                self._GUI_manager.set_models_polygon_mode(GL.GL_LINE)

            imgui.menu_item('Fill polygons')
            if imgui.is_item_clicked():
                log.info("Rendering filled polygons")
                self._GUI_manager.set_models_polygon_mode(GL.GL_FILL)

            imgui.separator()
            program_view_mode = self._GUI_manager.get_program_view_mode()
            if program_view_mode == '3D':
                imgui.menu_item('Change to 2D view')
            elif program_view_mode == '2D':
                imgui.menu_item('Change to 2D view')
            else:
                raise ValueError('That mode is not configured yet.')

            imgui.end_menu()

    def __edit_menu(self):
        """
        Options that appear when opening the Edit option from the main menu bar.
        """
        if imgui.begin_menu('Edit', True):
            imgui.menu_item('Undo', 'CTRL+Z', False, True)
            if imgui.is_item_clicked():
                self._GUI_manager.undo_action()

            imgui.separator()
            imgui.menu_item('Zoom In', None, False, True)
            imgui.menu_item('Zoom Out', None, False, True)

            imgui.end_menu()
