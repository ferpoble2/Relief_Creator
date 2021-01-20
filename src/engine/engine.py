"""
File that contains the program class, class that will be the main class of the program.
"""

import glfw
from threading import Thread

from src.engine.GUI.guimanager import GUIManager
from src.engine.controller.controller import Controller
from src.engine.render.render import Render
from src.engine.scene.scene import Scene
from src.engine.settings import Settings
from src.utils import get_logger

log = get_logger(module='ENGINE')


# noinspection PyMethodMayBeStatic
class Engine:
    """
    Main class of the program, controls and connect every component of the program.
    """

    def __init__(self):
        """
        Constructor of the program.
        """
        self.render = Render()
        self.gui_manager = GUIManager()
        self.window = None
        self.scene = Scene()
        self.controller = Controller()
        self.program = None

        self.__pending_task_list = []
        self.__threads_list = []

    def add_zoom(self) -> None:
        """
        Add zoom to the current map being watched.

        Returns: None
        """
        self.program.add_zoom()
        self.scene.update_models_projection_matrix()

    def add_vertex_to_active_polygon(self, position_x: int, position_y: int) -> None:
        """
        Ask the scene to add a vertex in the active polygon of the engine.

        Args:
            position_x: Position X of the point
            position_y: Position Y of the point (from top to bottom)

        Returns: None
        """
        try:
            self.scene.add_vertex_to_active_polygon(position_x, position_y)
        except AssertionError as e:
            log.debug(e)
            self.set_modal_text('Error', 'Error creating polygon. \n\nis a model loaded in the program?')

    def get_render_settings(self):
        """
        Return a dictionary with the settings related to the render.

        Returns: Dictionary with the render settings
        """
        return {
            "LINE_WIDTH": Settings.LINE_WIDTH,
            "POLYGON_LINE_WIDTH": Settings.POLYGON_LINE_WIDTH,
            "QUALITY": Settings.QUALITY
        }

    def are_frames_fixed(self) -> bool:
        """
        Return if the frames are fixed or not in the application.
        Returns: boolean indicating if the frames are fixed
        """
        return Settings.FIXED_FRAMES

    def change_color_of_polygon(self, polygon_id: str, color: list) -> None:
        """
        Change the color of the polygon with the specified id.

        Only change the color of the lines of the polygon.

        The colors must be defined in the order RGBA and with values between 0 and 1.

        Args:
            polygon_id: Id of the polygon to change the color.
            color: List-like object with the colors to use.

        Returns: None
        """
        self.scene.change_color_of_polygon(polygon_id, color)

    def change_color_file_with_dialog(self) -> None:
        """
        Change the color file (CPT file) to the one selected.
        This change all the models using the color file.

        Returns: None
        """
        self.program.change_cpt_file_with_dialog()

    def update_scene_models_colors(self):
        """
        Update the colors of the models in the scene with the colors that are
        in the ctp file stored in the program.

        Returns: None
        """
        self.scene.update_models_colors()

    def change_height_window(self, height: int) -> None:
        """
        Change the engine settings height for the windows.
        Args:
            height: New height

        Returns: None
        """
        Settings.HEIGHT = height

    def change_quality(self, quality: int) -> None:
        """
        Change the quality used to render the maps.

        Args:
            quality: Quality to use in the rendering process

        Returns: None
        """
        Settings.QUALITY = quality

    def change_width_window(self, width: int) -> None:
        """
        Change the engine settings width for the windows
        Args:
            width: New width

        Returns: None
        """
        Settings.WIDTH = width

    def fix_frames(self, fix: bool) -> None:
        """
        Fixes/unfix the frames in the application.
        Args:
            fix: boolean indicating if fix or not the frames.

        Returns: None
        """
        Settings.fix_frames(fix)

    def get_polygon_list(self) -> list:
        """
        Get the list of polygons currently being used by the program.

        Returns: list of polygons in the program
        """
        return self.scene.get_polygon_list()

    def get_active_polygon_id(self) -> str:
        """
        Get the id of the active polygon.

        Returns: id of the active polygon
        """
        return self.program.get_active_polygon_id()

    def set_active_polygon(self, polygon_id: str) -> None:
        """
        Set a new active polygon on the program.

        Args:
            polygon_id: ID of the polygon

        Returns: None
        """
        self.program.set_active_polygon(polygon_id)

    def get_active_model_id(self) -> str:
        """
        Returns the active model being used by the program.

        Returns: active model id
        """
        return self.program.get_active_model()

    def get_active_tool(self) -> str:
        """
        Get the active tool in the program.

        Returns: String with the active tool being used.
        """
        return self.program.get_active_tool()

    def get_clear_color(self) -> list:
        """
        Get the clear color used.
        Returns:list with the clear color

        """
        return Settings.CLEAR_COLOR

    def get_cpt_file(self) -> str:
        """
        Get the CTP file currently being used in the program
        Returns: String with the path to the file

        """
        return self.program.get_cpt_file()

    def get_float_bytes(self) -> int:
        """
        Return the number of bytes used to represent a float number in opengl.

        Returns: number of bytes used to represent a float.
        """
        return Settings.FLOAT_BYTES

    def get_font_size(self) -> int:
        """
        Get the font size to use in the program.
        Returns: font size
        """
        return Settings.FONT_SIZE

    def get_gui_setting_data(self) -> dict:
        """
        Get the GUI setting data.
        Returns: dict with the data

        """
        return {
            'LEFT_FRAME_WIDTH': Settings.LEFT_FRAME_WIDTH,
            'TOP_FRAME_HEIGHT': Settings.TOP_FRAME_HEIGHT,
            'MAIN_MENU_BAR_HEIGHT': Settings.MAIN_MENU_BAR_HEIGHT
        }

    def get_map_position(self) -> list:
        """
        Get the map position on the program.

        Returns: List with the position of the map.
        """
        return self.program.get_map_position()

    def get_quality(self) -> int:
        """
        Get the quality value stored in the settings.

        Returns: Quality setting
        """
        return Settings.QUALITY

    def get_scene_setting_data(self) -> dict:
        """
        Get the scene setting data.
        Returns: dict with the data
        """
        return {
            'SCENE_BEGIN_X': Settings.SCENE_BEGIN_X, 'SCENE_BEGIN_Y': Settings.SCENE_BEGIN_Y,
            'SCENE_WIDTH_X': Settings.SCENE_WIDTH_X, 'SCENE_HEIGHT_Y': Settings.SCENE_HEIGHT_Y
        }

    def get_view_mode(self) -> str:
        """
        Get the view mode stored in the settings.

        Returns: View mode
        """
        return Settings.VIEW_MODE

    def get_window_setting_data(self) -> dict:
        """
        Get the window setting data.
        Returns: dict with the data
        """
        return {
            'HEIGHT': Settings.HEIGHT,
            'WIDTH': Settings.WIDTH,
            'MAX_WIDTH': Settings.MAX_WIDTH,
            'MAX_HEIGHT': Settings.MAX_HEIGHT,
            'MIN_WIDTH': Settings.MIN_WIDTH,
            'MIN_HEIGHT': Settings.MIN_HEIGHT
        }

    def optimize_gpu_memory(self) -> None:
        """
        Call the scene to optimize the GPU memory.

        Make an asyncronic call, setting the loading screen.

        Returns: None
        """
        log.debug("Optimizing gpu memory")
        self.program.set_loading(True)
        self.set_loading_message("Deleting triangles from the memory")

        def then_routine():
            self.program.set_loading(False)

        self.scene.optimize_gpu_memory_async(then_routine)

    def get_zoom_level(self) -> float:
        """
        Get the zoom level currently being used in the program.

        Returns: Zoom level

        """
        return self.program.get_zoom_level()

    def initialize(self, engine: 'Engine', program: 'Program') -> None:
        """
        Initialize the components of the program.
        Returns: None

        Args:
            program: Program that runs the engine and the application.
            engine: Engine to initialize.
        """
        log.info('Starting Program')
        self.program = program

        # GLFW CODE
        # ---------
        log.debug("Creating windows.")
        self.window = self.render.init("Relief Creator", engine)

        # GUI CODE
        # --------
        log.debug("Loading GUI")
        self.gui_manager.initialize(self.window, engine)
        self.gui_manager.add_frames(self.gui_manager.get_frames(self.gui_manager))

        # CONTROLLER CODE
        # ---------------
        self.controller.init(engine)
        glfw.set_key_callback(self.window, self.controller.get_on_key_callback())
        glfw.set_window_size_callback(self.window, self.controller.get_resize_callback())
        glfw.set_mouse_button_callback(self.window, self.controller.get_mouse_button_callback())
        glfw.set_cursor_pos_callback(self.window, self.controller.get_cursor_position_callback())

        # SCENE CODE
        # ----------
        self.scene.initialize(engine)

    def is_program_loading(self) -> bool:
        """
        Return if the program is loading or not.

        Returns: Boolean representing if the program is running or not.
        """
        return self.program.is_loading()

    def less_zoom(self) -> None:
        """
        Reduce on 1 the level of zoom.

        Returns: None
        """
        self.program.less_zoom()
        self.scene.update_models_projection_matrix()

    def move_scene(self, x_movement: int, y_movement: int) -> None:
        """
        Tell the scene to move given the parameters specified.

        Args:
            x_movement: Movement in the x-axis
            y_movement: Movement in the y-axis

        Returns: None
        """
        self.scene.move_models(x_movement, y_movement)

    def refresh_with_model_2d(self, path_color_file: str, path_model: str, model_id: str = 'main') -> None:
        """
        Refresh the scene creating a 2D model with the parameters given.

        Args:
            model_id: Model id to use in the new model.
            path_color_file: Path to the color file to use.
            path_model: Path to the model file (NetCDF) to use.

        Returns: none
        """

        def then_routine():
            self.program.set_active_model(model_id)
            self.program.set_loading(False)

        self.program.set_loading(True)
        self.set_loading_message("Please wait a moment...")

        try:
            self.scene.refresh_with_model_2d_async(path_color_file, path_model, model_id, then_routine)

        except OSError as e:
            self.program.set_loading(False)
            raise e

        except KeyError as e:
            self.program.set_loading(False)
            raise e

    def reload_models(self) -> None:
        """
        Ask the Scene to reload the models to better the definitions.

        Returns: None
        """
        self.program.set_loading(True)
        self.set_loading_message("Please wait a moment...")

        def then_routine():
            self.program.set_loading(False)

        self.scene.reload_models_async(then_routine)

    def create_new_polygon(self) -> str:
        """
        Create a new polygon on the scene.

        Returns: the id of the new polygon
        """
        return self.scene.create_new_polygon()

    def delete_polygon_by_id(self, polygon_id: str) -> None:
        """
        Delete the polygon with the specified id from the scene

        Args:
            polygon_id: Polygon id to use to delete

        Returns: None
        """
        self.scene.delete_polygon_by_id(polygon_id)

    def reset_zoom_level(self) -> None:
        """
        Reset the zoom level of the program.

        Returns: None
        """
        self.program.reset_zoom_level()

    def run(self) -> None:
        """
        Run the program
        Returns: None
        """
        log.debug("Starting main loop.")
        while not glfw.window_should_close(self.window):
            self.update_pending_tasks()
            self.update_threads()
            self.render.on_loop([lambda: self.scene.draw()])

        glfw.terminate()

    def set_active_tool(self, tool: str) -> None:
        """
        Set the active tool in the program.

        Args:
            tool: String representing the new tool.

        Returns: None
        """
        self.program.set_active_tool(tool)

    def set_loading_message(self, new_msg: str) -> None:
        """
        Change the loading message shown on the screen.

        Args:
            new_msg: New message to show

        Returns: None
        """
        self.gui_manager.set_loading_message(new_msg)

    def set_map_position(self, new_position: list) -> None:
        """
        Tell the program the new position of the map.

        Args:
            new_position: New position to use.

        Returns: None
        """
        self.program.set_map_position(new_position)

    def set_task_for_next_frame(self, task: callable) -> None:
        """
        Add a task to do in the next frame.

        Args:
            task: Callable to call in the next frame.

        Returns: None
        """
        log.debug("Setting task for next frame")
        self.__pending_task_list.append({
            'task': task,
            'frames': 2  # need to be 2 to really wait one full frame
        })

    def set_task_with_loading_frame(self, task: callable) -> None:
        """
        Set a task to be executed at the end of the next frame. Also configures the loading setting of
        the program to show the loading frame on the screen.

        Args:
            task: Task to be called in while showing a loading frame.

        Returns: None
        """
        self.program.set_loading(True)

        def task_loading():
            task()
            self.program.set_loading(False)

        self.set_task_for_next_frame(task_loading)

    def load_netcdf_file_with_dialog(self) -> None:
        """
        Open a dialog to load a new netcdf model into the program.

        Returns: None
        """
        self.program.load_netcdf_file_with_dialog()

    def set_modal_text(self, title_modal, msg) -> None:
        """
        Set a modal in the program.

        Args:
            title_modal: title of the modal
            msg: message to show in the modal

        Returns: None
        """
        self.gui_manager.set_modal_text(title_modal, msg)

    def set_thread_task(self, parallel_task, then) -> None:
        """
        Add and start a new thread with the current task. At the end of the thread, the then
        function is called.

        Args:
            parallel_task: Task to be executed in parallel
            then: Task to be executed in the main thread after the parallel task

        Returns: None
        """
        # Create and start the thread
        thread = Thread(target=parallel_task)
        thread.start()

        # Add thread to the list
        self.__threads_list.append(
            {'thread': thread,
             'then_func': then}
        )

    def update_pending_tasks(self) -> None:
        """
        Update the pending tasks.

        Subtract one from the frames of the tasks and execute them if the number
        of frames to wait is zero.

        Returns: None
        """
        to_delete = []

        # check on the tasks
        for task in self.__pending_task_list:
            log.debug(f"Pending tasks: {self.__pending_task_list}")

            # Subtract one frame from the task
            task['frames'] -= 1

            # execute it if frames to wait is zero
            if task['frames'] == 0:
                task['task']()
                to_delete.append(task)

        # delete tasks already executed
        for task in to_delete:
            self.__pending_task_list.remove(task)

    def update_scene_values(self) -> None:
        """
        Update the configuration values related to the scene.
        Returns: None
        """
        Settings.update_scene_values()

    def update_threads(self) -> None:
        """
        Checks on the threads of the engine, deleting them if they finished and executing the
        task configured for them after.

        Returns: None
        """
        to_delete = []
        for thread_pair in self.__threads_list:
            if not thread_pair['thread'].is_alive():
                to_delete.append(thread_pair)
                thread_pair['then_func']()

        for thread_ended in to_delete:
            log.debug("Thread ended")
            self.__threads_list.remove(thread_ended)
