"""
Main menu bar frame in the GUI
"""
from src.engine.GUI.frames.frame import Frame
from src.utils import get_logger

import imgui
import shapefile
import OpenGL.GL as GL

log = get_logger(module="MAIN MENU BAR")


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
                try:
                    self._GUI_manager.load_netcdf_file_with_dialog()

                except KeyError:
                    log.debug("Error reading files, KeyError")
                    self._GUI_manager.set_modal_text("Error", "Error reading the selected files (KeyError)")

                except OSError:
                    log.debug("Error reading files, OSError")
                    self._GUI_manager.set_modal_text("Error", "Error reading the selected files (OSError)")

            imgui.menu_item('Change CPT file...', 'Ctrl+T', False, True)
            if imgui.is_item_clicked():

                try:
                    self._GUI_manager.change_color_file_with_dialog()

                except KeyError as e:
                    log.exception(f"Error reading files: {e}")
                    self._GUI_manager.set_modal_text("Error", "Error reading color file (KeyError)")

                except IOError as e:
                    log.exception(f"Error reading files: {e}")
                    self._GUI_manager.set_modal_text("Error", "Error reading color file (IOError)")

                except TypeError as e:
                    log.exception(f"Error reading files: {e}")
                    self._GUI_manager.set_modal_text("Error", "Error reading color file (TypeError)")

            imgui.separator()
            imgui.menu_item('Load shapefile file...', 'Ctrl+L', False, True)
            if imgui.is_item_clicked():
                log.debug('Clicked load shapefile...')

                # check that a map is loaded in the program
                if self._GUI_manager.get_active_model_id() is None:
                    self._GUI_manager.set_modal_text('Error', 'Load a netcdf file before loading a polygon.')

                # in case all check pass
                else:
                    try:
                        self._GUI_manager.load_shapefile_file_with_dialog()
                        imgui.close_current_popup()

                    except shapefile.ShapefileException as e:
                        log.error(e)
                        self._GUI_manager.set_modal_text('Error', 'Error loading file. (ShapefileException)')

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
