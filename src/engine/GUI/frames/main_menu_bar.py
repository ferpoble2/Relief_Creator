"""
Main menu bar frame in the GUI
"""
from src.engine.GUI.frames.frame import Frame
from src.utils import get_logger
from src.engine.GUI.guimanager import GUIManager
import imgui

log = get_logger(module="MAIN MENU BAR")


class MainMenuBar(Frame):
    """
    Frame that controls the top menu bar of the application.
    """

    def __init__(self, gui_manager: GUIManager):
        """
        Constructor of the class.

        Args:
            gui_manager: GuiManager of the application.
        """
        super().__init__()
        self.__GUI_manager: GUIManager = gui_manager

    def render(self) -> None:
        """
        Render the main menu bar on the screen.
        Returns: None
        """

        if imgui.begin_main_menu_bar():
            # first menu dropdown
            if imgui.begin_menu('File', True):
                imgui.menu_item('New', 'Ctrl+N', False, True)
                imgui.menu_item('Open ...', 'Ctrl+O', False, True)

                # submenu
                if imgui.begin_menu('Open Recent', True):
                    imgui.menu_item('doc.txt', None, False, True)
                    imgui.end_menu()

                imgui.end_menu()

            # second menu dropdown
            if imgui.begin_menu('Edit', True):
                imgui.menu_item('Zoom In', None, False, True)
                imgui.menu_item('Zoom Out', None, False, True)

                imgui.end_menu()

            # third menu dropdown
            if imgui.begin_menu('View'):

                imgui.menu_item('Fix Windows Positions.')
                if imgui.is_item_clicked():
                    self.__GUI_manager.fix_frame_position(True)

                imgui.menu_item('Unfix Windows Positions.')
                if imgui.is_item_clicked():
                    self.__GUI_manager.fix_frame_position(False)

                imgui.end_menu()

            imgui.end_main_menu_bar()
