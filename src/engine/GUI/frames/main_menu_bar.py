"""
Main menu bar frame in the GUI
"""
from src.engine.GUI.frames.frame import Frame
from src.utils import get_logger

import imgui
import OpenGL.GL as GL
import easygui

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
                    path_color_file = easygui.fileopenbox('Select CPT file...')
                    log.debug(f"path_model: {path_color_file}")

                    try:
                        self._GUI_manager.change_color_file(path_color_file)

                    except KeyError:
                        log.debug("Error reading files or creating models, KEYError")
                        self.error_file = True

                    except OSError:
                        log.debug("Error reading files, OSError")
                        self.error_file = True

                imgui.end_menu()

            # second menu dropdown
            if imgui.begin_menu('Edit', True):
                imgui.menu_item('Zoom In', None, False, True)
                imgui.menu_item('Zoom Out', None, False, True)

                imgui.end_menu()

            # third menu dropdown
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
                    self._GUI_manager.set_polygon_mode(GL.GL_POINT)

                imgui.menu_item('Use wireframes')
                if imgui.is_item_clicked():
                    log.info("Rendering wireframes")
                    self._GUI_manager.set_polygon_mode(GL.GL_LINE)

                imgui.menu_item('Fill polygons')
                if imgui.is_item_clicked():
                    log.info("Rendering filled polygons")
                    self._GUI_manager.set_polygon_mode(GL.GL_FILL)

                imgui.end_menu()

            imgui.end_main_menu_bar()
