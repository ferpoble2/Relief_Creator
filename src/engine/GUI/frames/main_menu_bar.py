"""
Main menu bar frame in the GUI
"""
from src.engine.GUI.frames.frame import Frame
from src.utils import get_logger
from src.engine.GUI.guimanager import GUIManager
from src.engine.scene.scene import Scene

import imgui
import OpenGL.GL as GL
import easygui

log = get_logger(module="MAIN MENU BAR")


class MainMenuBar(Frame):
    """
    Frame that controls the top menu bar of the application.
    """

    def __init__(self, gui_manager: GUIManager, scene: Scene):
        """
        Constructor of the class.

        Args:
            scene: Scene of the application.
            gui_manager: GuiManager of the application.
        """
        super().__init__()
        self.__GUI_manager: GUIManager = gui_manager
        self.scene: Scene = scene

        self.fixed_position = True

        self.error_file = False

    def render(self) -> None:
        """
        Render the main menu bar on the screen.
        Returns: None
        """

        if imgui.begin_main_menu_bar():
            # first menu dropdown
            if imgui.begin_menu('File', True):
                imgui.menu_item('Open file', 'Ctrl+O', False, True)
                if imgui.is_item_clicked():
                    log.info("Open File Dialog")
                    path_model = easygui.fileopenbox('Select NETCDF file')
                    path_color_file = easygui.fileopenbox('Select CTP file')

                    log.debug(f"path_model: {path_model}")
                    log.debug(f"path_color_File: {path_color_file}")

                    if path_model is not None and path_color_file is not None:
                        try:
                            self.scene.refresh_with_model_2d(path_color_file, path_model)

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

                if self.fixed_position:
                    imgui.menu_item('Unfix Windows Positions')
                    if imgui.is_item_clicked():
                        self.__GUI_manager.fix_frames_position(False)
                        self.fixed_position = False

                else:
                    imgui.menu_item('Fix Windows Positions')
                    if imgui.is_item_clicked():
                        self.__GUI_manager.fix_frames_position(True)
                        self.fixed_position = True

                imgui.separator()

                imgui.menu_item('Use points')
                if imgui.is_item_clicked():
                    log.info("Rendering points")
                    self.scene.set_polygon_mode(GL.GL_POINT)

                imgui.menu_item('Use wireframes')
                if imgui.is_item_clicked():
                    log.info("Rendering wireframes")
                    self.scene.set_polygon_mode(GL.GL_LINE)

                imgui.menu_item('Fill polygons')
                if imgui.is_item_clicked():
                    log.info("Rendering filled polygons")
                    self.scene.set_polygon_mode(GL.GL_FILL)

                imgui.end_menu()

            imgui.end_main_menu_bar()

            # Pop-ups windows
            # ---------------
            if self.error_file:
                log.debug("Showing error pop up from reading file.")
                imgui.open_popup("Input Error")
                self.error_file = False

            if imgui.begin_popup_modal("Input Error")[0]:
                imgui.text("Error reading the selected files.")
                if imgui.button("Accept"):
                    imgui.close_current_popup()
                imgui.end_popup()
