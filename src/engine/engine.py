"""
File that contains the program class, class that will be the main class of the program.
"""

import glfw

from src.engine.controller.controller import Controller
from src.engine.GUI.guimanager import GUIManager
from src.engine.process_manager import ProcessManager
from src.engine.render.render import Render
from src.engine.scene.scene import Scene
from src.engine.settings import Settings
from src.engine.thread_manager import ThreadManager

from src.input.shapefile_importer import ShapefileImporter
from src.output.netcdf_exporter import NetcdfExporter
from src.output.shapefile_exporter import ShapefileExporter
from src.utils import get_logger

from src.error.line_intersection_error import LineIntersectionError
from src.error.model_transformation_error import ModelTransformationError
from src.error.repeated_point_error import RepeatedPointError
from src.error.scene_error import SceneError
from src.error.not_enought_points_error import NotEnoughPointsError
from src.error.netcdf_import_error import NetCDFImportError

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
        self.scene = Scene(self)
        self.controller = Controller(self)
        self.program = None
        self.__process_manager = ProcessManager()
        self.__thread_manager = ThreadManager()

        # note: the order of definition of the components matters.

        self.__pending_task_list = []

    def __update_pending_tasks(self) -> None:
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

    def get_camera_settings(self) -> dict:
        """
        Get all the settings related to the camera.

        Returns: Dictionary with the settings related to the camera.
        """
        return {
            'FIELD_OF_VIEW': Settings.FIELD_OF_VIEW,
            'PROJECTION_NEAR': Settings.PROJECTION_NEAR,
            'PROJECTION_FAR': Settings.PROJECTION_FAR
        }

    def add_new_vertex_to_active_polygon_using_window_coords(self, position_x: int, position_y: int) -> None:
        """
        Ask the scene to add a vertex in the active polygon of the engine.

        Args:
            position_x: Position X of the point
            position_y: Position Y of the point (from top to bottom)

        Returns: None
        """
        try:
            self.scene.add_new_vertex_to_active_polygon_using_window_coords(position_x, position_y)
        except AssertionError as e:
            log.error(e)
            self.set_modal_text('Error', f'Error creating polygon. \n\n{e}')

    def add_zoom(self) -> None:
        """
        Add zoom to the current map being watched.

        Returns: None
        """
        self.program.add_zoom()
        self.scene.update_models_projection_matrix()

    def are_frames_fixed(self) -> bool:
        """
        Return if the frames are fixed or not in the application.
        Returns: boolean indicating if the frames are fixed
        """
        return Settings.FIXED_FRAMES

    def calculate_max_min_height(self, model_id: str, polygon_id: str) -> tuple:
        """
        Ask the scene for max and min values of the vertices that are inside the polygon.

        Args:
            model_id: ID of the model to use.
            polygon_id: ID of the polygon to use.

        Returns: tuple with the max and min value.
        """

        try:
            return self.scene.calculate_max_min_height(model_id, polygon_id)

        except SceneError as e:
            if e.code == 1:
                self.set_modal_text('Error',
                                    'The polygon is not planar. Try using a planar polygon.')
                return None, None
            elif e.code == 2:
                self.set_modal_text('Error',
                                    'The polygon must have at least 3 points to be able to '
                                    'calculate the information.')
                return None, None
            elif e.code == 3:
                self.set_modal_text('Error',
                                    'The current model is not supported to use to update the '
                                    'height of the vertices, try using another type of model.')
                return None, None
            else:
                raise e

    def change_color_file_with_dialog(self) -> None:
        """
        Change the color file (CPT file) to the one selected.
        This change all the models using the color file.

        Returns: None
        """
        try:
            self.program.change_cpt_file_with_dialog()
        except FileNotFoundError:
            self.set_modal_text('Error', 'File not loaded.')
        except IOError:
            self.set_modal_text('Error', 'File is not a cpt file.')

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

    def change_dot_color_of_polygon(self, polygon_id: str, color: list) -> None:
        """
        Change the color of the dots of the polygon with the specified id.

        Only change the color of the dots of the polygon.

        The colors must be defined in the order RGBA and with values between 0 and 1.

        Args:
            polygon_id: Id of the polygon to change the color.
            color: List-like object with the colors to use.

        Returns: None
        """
        self.scene.change_dot_color_of_polygon(polygon_id, color)

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

    def create_new_polygon(self) -> str:
        """
        Create a new polygon on the scene.

        Returns: the id of the new polygon
        """
        return self.scene.create_new_polygon()

    def delete_parameter_from_polygon(self, polygon_id: str, key: str) -> None:
        """
        Delete a parameter from a polygon.

        Args:
            polygon_id: ID of the polygon.
            key: Parameter to be deleted.

        Returns: None
        """
        self.scene.delete_polygon_param(polygon_id, key)

    def delete_polygon_by_id(self, polygon_id: str) -> None:
        """
        Delete the polygon with the specified id from the scene

        Args:
            polygon_id: Polygon id to use to delete

        Returns: None
        """
        self.scene.delete_polygon_by_id(polygon_id)

    def disable_glfw_keyboard_callback(self) -> None:
        """
        Disable the glfw callback defined in the controller.

        The GUI callback is not affected.

        Returns: None
        """
        self.controller.disable_glfw_keyboard_callback()

    def enable_glfw_keyboard_callback(self) -> None:
        """
        Enable the glfw callback defined in the controller.

        The GUI callback is not affected.

        Returns: None
        """
        self.controller.enable_glfw_keyboard_callback()

    def export_model_as_netcdf(self, model_id: str) -> None:
        """
        Save the information of a model in a netcdf file.

        Args:
            model_id: ID of the model to export.

        Returns: None
        """

        # select a directory to store the file.
        file = self.program.open_file_save_box_dialog('Select a directory and filename for the shapefile file.',
                                                      'Relief Creator',
                                                      'Model')

        # ask the scene for information
        vertices = self.scene.get_map2dmodel_vertices_array(model_id)

        # ask the output to write the file
        NetcdfExporter().export_model_vertices_to_netcdf_file(vertices, file)

    def export_polygon_list_id(self, polygon_id_list: list, filename='polygons') -> None:
        """
        Export the polygons to a shapefile file.

        Args:
            filename: Name to use as placeholder in the box to store files.
            polygon_id_list: List with the polygons IDs.

        Returns: None
        """
        points_list = []
        parameters_list = []
        names_list = []
        for polygon_id in polygon_id_list:
            points_list.append(self.scene.get_point_list_from_polygon(polygon_id))
            parameters_list.append(dict(self.scene.get_polygon_params(polygon_id)))
            names_list.append(self.scene.get_polygon_name(polygon_id))

        try:
            file = self.program.open_file_save_box_dialog('Select a directory and filename for the shapefile file.',
                                                          'Relief Creator',
                                                          filename)
        except ValueError:
            self.set_modal_text('Error', 'Polygons not exported.')
            return

        try:
            ShapefileExporter().export_list_of_polygons(points_list,
                                                        parameters_list,
                                                        names_list,
                                                        file)
        except NotEnoughPointsError:
            self.set_modal_text('Error', 'One or more polygons does not have enough '
                                         'points to be exported.')
            return

        self.set_modal_text('Information', 'Polygons exported successfully.')

    def export_polygon_with_id(self, polygon_id: str) -> None:
        """
        Export the polygon with the given ID to a shapefile file

        Args:
            polygon_id: Id of the polygon to export to shapefile

        Returns: None
        """

        # ask for the points of the polygon
        points = self.scene.get_point_list_from_polygon(polygon_id)

        try:
            file = self.program.open_file_save_box_dialog('Select a filename and directory for the new polygon',
                                                          'Relief Creator',
                                                          self.scene.get_polygon_name(polygon_id))
        except ValueError:
            self.set_modal_text('Error', 'Polygon not exported.')
            return

        # ask the exporter to export the list of points
        try:
            ShapefileExporter().export_polygon_to_shapefile(points,
                                                            file,
                                                            self.scene.get_polygon_name(polygon_id),
                                                            dict(self.scene.get_polygon_params(polygon_id)))
        except NotEnoughPointsError:
            self.set_modal_text("Error", "The polygon does not have enough points.")
            return

        self.set_modal_text('Information', 'Polygon exported successfully')

    def fix_frames(self, fix: bool) -> None:
        """
        Fixes/unfix the frames in the application.
        Args:
            fix: boolean indicating if fix or not the frames.

        Returns: None
        """
        Settings.fix_frames(fix)

    def get_active_model_id(self) -> str:
        """
        Returns the active model being used by the program.

        Returns: active model id
        """
        return self.program.get_active_model()

    def get_active_polygon_id(self) -> str:
        """
        Get the id of the active polygon.

        Returns: id of the active polygon
        """
        return self.program.get_active_polygon_id()

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

    def get_extra_reload_proportion_setting(self) -> float:
        """
        Get the extra reload proportion stored in the settings of the program.

        Returns: Float with the value of the extra reload proportion.
        """
        return Settings.EXTRA_RELOAD_PROPORTION

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

    def get_gui_key_callback(self) -> callable:
        """
        Get the key callback used by the gui

        Returns: Function used as the key callback in the gui
        """
        return self.gui_manager.get_gui_key_callback()

    def get_gui_scroll_callback(self):
        """
        Ask the gui manager for the callback used in the scrolling.

        Returns: Function used in the callback.
        """
        return self.gui_manager.get_gui_mouse_scroll_callback()

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

    def get_camera_data(self) -> dict:
        """
        Ask the scene for the camera data.

        Returns: Dictionary with the data related to the camera.
        """
        return self.scene.get_camera_data()

    def get_parameters_from_polygon(self, polygon_id: str) -> list:
        """
        Ask the scene for the parameters of certain polygon.

        Args:
            polygon_id: ID of the polygon to ask for

        Returns: List with the parameters of the polygon.
        """
        return self.scene.get_polygon_params(polygon_id)

    def get_polygon_id_list(self) -> list:
        """
        Get the full list of polygon ids currently being used on the program.

        Returns: list of polygons in the program
        """
        return self.scene.get_polygon_id_list()

    def get_polygon_name(self, polygon_id: str) -> str:
        """
        Get the name of a polygon given its id

        Args:
            polygon_id: Id of the polygon

        Returns: Name of the polygon
        """
        return self.scene.get_polygon_name(polygon_id)

    def get_quality(self) -> int:
        """
        Get the quality value stored in the settings.

        Returns: Quality setting
        """
        return Settings.QUALITY

    def get_render_settings(self):
        """
        Return a dictionary with the settings related to the render.

        Returns: Dictionary with the render settings
        """
        return {
            "LINE_WIDTH": Settings.LINE_WIDTH,
            "POLYGON_LINE_WIDTH": Settings.POLYGON_LINE_WIDTH,
            "QUALITY": Settings.QUALITY,
            "DOT_SIZE": Settings.DOT_SIZE,
            "POLYGON_DOT_SIZE": Settings.POLYGON_DOT_SIZE,
            "ACTIVE_POLYGON_LINE_WIDTH": Settings.ACTIVE_POLYGON_LINE_WIDTH
        }

    def get_scene_setting_data(self) -> dict:
        """
        Get the scene setting data.
        Returns: dict with the data
        """
        return {
            'SCENE_BEGIN_X': Settings.SCENE_BEGIN_X, 'SCENE_BEGIN_Y': Settings.SCENE_BEGIN_Y,
            'SCENE_WIDTH_X': Settings.SCENE_WIDTH_X, 'SCENE_HEIGHT_Y': Settings.SCENE_HEIGHT_Y
        }

    def get_tool_title_font_size(self) -> int:
        """
        Get the font size to use for the tool titles.

        Returns: Int with the font size to use.
        """
        return Settings.TOOL_TITLE_FONT_SIZE

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

    def get_zoom_level(self) -> float:
        """
        Get the zoom level currently being used in the program.

        Returns: Zoom level

        """
        return self.program.get_zoom_level()

    # noinspection PyUnresolvedReferences
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
        self.gui_manager.initialize(self.window, engine, self.gui_manager)

        # CONTROLLER CODE
        # ---------------
        glfw.set_key_callback(self.window, self.controller.get_on_key_callback())
        glfw.set_window_size_callback(self.window, self.controller.get_resize_callback())
        glfw.set_mouse_button_callback(self.window, self.controller.get_mouse_button_callback())
        glfw.set_cursor_pos_callback(self.window, self.controller.get_cursor_position_callback())
        glfw.set_scroll_callback(self.window, self.controller.get_mouse_scroll_callback())

    def interpolate_points(self, polygon_id: str, model_id: str, distance: float, type_interpolation: str) -> None:
        """
        Ask the scene to interpolate the points using the specified parameters.

        Args:
            type_interpolation: Type of interpolation to use.
            polygon_id: ID of the polygon to use.
            model_id: ID of the model to use.
            distance: Distance to use for the interpolation.

        Returns: None
        """
        self.scene.interpolate_points(polygon_id, model_id, distance, type_interpolation)

    def is_mouse_hovering_frame(self) -> bool:
        """
        Ask the GUIManager if the mouse is hovering a frame.

        Returns: Boolean indicating if mouse is hovering a frame or not.
        """
        return self.gui_manager.is_mouse_inside_frame()

    def is_polygon_planar(self, polygon_id: str) -> bool:
        """
        Ask to the scene if the polygon is planar or not.

        Args:
            polygon_id: Id of the polygon

        Returns: Boolean indicating if the polygon is planar or not
        """
        return self.scene.is_polygon_planar(polygon_id)

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

    def load_netcdf_file_with_dialog(self) -> None:
        """
        Open a dialog to load a new netcdf model into the program.

        Returns: None
        """
        try:
            self.program.load_netcdf_file_with_dialog()
        except FileNotFoundError as e:
            log.exception(e)
            self.set_modal_text('Error', 'File not loaded.')

    def load_polygon_from_shapefile(self, filename: str) -> None:
        """
        Load the data from a shapefile file and tell the scene to create a polygon with it.

        Args:
            filename: Name of the shapefile file.

        Returns: None
        """
        polygons_point_list, polygons_param_list = ShapefileImporter().get_polygon_information(filename)

        if polygons_point_list is None and polygons_param_list is None:
            self.set_modal_text('Error', 'An error happened while loading file.')
            return

        if self.get_active_model_id() is None:
            self.set_modal_text('Error', 'Please load a model before loading polygons.')
            return

        error_number = 0

        for ind in range(len(polygons_point_list)):
            errors = False

            new_polygon_id = self.scene.create_new_polygon()
            self.set_active_polygon(new_polygon_id)

            for k, v in list(polygons_param_list[ind].items()):
                self.set_new_parameter_to_polygon(new_polygon_id, k, v)

            # add the points to the polygon
            for point in polygons_point_list[ind]:  # shapefile polygons are closed, so we do not need the last point

                try:
                    self.scene.add_new_vertex_to_active_polygon_using_real_coords(point[0], point[1])

                except LineIntersectionError as e:
                    log.error(e)
                    errors = True
                    self.scene.delete_polygon_by_id(new_polygon_id)
                    self.set_active_polygon(None)
                    error_number += 1
                    break

                except RepeatedPointError as e:
                    log.error(e)
                    errors = True
                    self.scene.delete_polygon_by_id(new_polygon_id)
                    self.set_active_polygon(None)
                    error_number += 1
                    break

            if not errors:
                # tell the gui manager that a new polygon was created
                log.debug('add polygon to the gui frames')
                self.gui_manager.add_imported_polygon(new_polygon_id)

        if error_number == 0:
            self.set_modal_text('Information', 'Shapefile loaded successfully')
        else:
            self.set_modal_text('Information', f'There was {error_number} polygons with errors that were not loaded.')

    def load_preview_interpolation_area(self, distance: float) -> None:
        """
        Ask the scene to load the interpolation area for the active polygon.

        Args:
            distance: Distance to use to calculate the interpolation area.

        Returns: None
        """
        self.scene.load_preview_interpolation_area(distance)

    def load_shapefile_file_with_dialog(self) -> None:
        """
        Call the program to open the dialog to load a shapefile file.

        Returns: None
        """
        try:
            self.program.load_shapefile_file_with_dialog()
        except FileNotFoundError as e:
            log.exception(e)
            self.set_modal_text('Error', 'File not loaded.')

    def move_scene(self, x_movement: int, y_movement: int) -> None:
        """
        Tell the scene to move given the parameters specified.

        Args:
            x_movement: Movement in the x-axis
            y_movement: Movement in the y-axis

        Returns: None
        """
        self.scene.move_models(x_movement, y_movement)

    def optimize_gpu_memory(self) -> None:
        """
        Call the scene to optimize the GPU memory.

        Make an asynchronous call, setting the loading screen.

        Returns: None
        """
        log.debug("Optimizing gpu memory")
        self.program.set_loading(True)
        self.set_loading_message("Deleting triangles from the memory")

        # noinspection PyMissingOrEmptyDocstring
        def then_routine():
            self.program.set_loading(False)

        self.scene.optimize_gpu_memory_async(then_routine)

    def refresh_with_model_2d(self, path_color_file: str, path_model: str) -> None:
        """
        Refresh the scene creating a 2D model with the parameters given.

        Args:
            path_color_file: Path to the color file to use.
            path_model: Path to the model file (NetCDF) to use.

        Returns: none
        """

        # noinspection PyMissingOrEmptyDocstring
        def then_routine(model_id):
            self.program.set_active_model(model_id)
            self.program.set_loading(False)

        self.program.set_loading(True)
        self.set_loading_message("Please wait a moment...")

        try:
            self.scene.refresh_with_model_2d_async(path_color_file, path_model, then_routine)

        except OSError:
            self.program.set_loading(False)
            self.set_modal_text('Error', 'Error reading selected file. Is the file a netcdf file?')

        except NetCDFImportError as e:
            self.program.set_loading(False)
            self.set_modal_text('Error', f'{e.get_code_message()}\n\n'
                                         f'Current keys on the file are: {list(e.data)}')

        except KeyError:
            self.program.set_loading(False)
            self.set_modal_text('Error', 'Error reading selected file. Is the key used in the file inside the '
                                         'list of keys?')

    def reload_models(self) -> None:
        """
        Ask the Scene to reload the models to better the definitions.

        Returns: None
        """
        self.program.set_loading(True)
        self.set_loading_message("Please wait a moment...")

        # noinspection PyMissingOrEmptyDocstring
        def then_routine():
            self.optimize_gpu_memory()  # async function
            # self.program.set_loading(False)

        self.scene.reload_models_async(then_routine)

    def remove_interpolation_preview(self, polygon_id: str) -> None:
        """
        Ask the scene to remove the interpolation area of the specified polygon.

        Args:
            polygon_id: Polygon if of the polygon to remove the area to.

        Returns: None
        """
        self.scene.remove_interpolation_preview(polygon_id)

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
            self.__update_pending_tasks()
            self.__thread_manager.update_threads()
            self.__process_manager.update_process()
            self.render.on_loop([lambda: self.scene.draw()])

        glfw.terminate()

    def set_active_polygon(self, polygon_id: str or None) -> None:
        """
        Set a new active polygon on the program. Set None to remove the active polygon.

        Args:
            polygon_id: ID of the polygon or None.

        Returns: None
        """
        self.program.set_active_polygon(polygon_id)

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

    def set_modal_text(self, title_modal, msg) -> None:
        """
        Set a modal in the program.

        Args:
            title_modal: title of the modal
            msg: message to show in the modal

        Returns: None
        """
        self.gui_manager.set_modal_text(title_modal, msg)

    # noinspection PyUnresolvedReferences
    def set_models_polygon_mode(self, polygon_mode: 'OGLConstant.IntConstant') -> None:
        """
        Call the scene to change the polygon mode used by the models.

        Args:
            polygon_mode: Polygon mode to use.

        Returns:
        """
        self.scene.set_models_polygon_mode(polygon_mode)

    def set_new_parameter_to_polygon(self, polygon_id: str, key: str, value: any) -> None:
        """
        Set a new parameter to an existent polygon.

        Args:
            value: value of the parameter.
            key: key of the new value.
            polygon_id: ID of the polygon.

        Returns: None
        """
        self.scene.set_polygon_param(polygon_id, key, value)

    def set_polygon_name(self, polygon_id: str, new_name: str) -> None:
        """
        Change the name of a polygon.

        Args:
            polygon_id: Old polygon id
            new_name: New polygon id

        Returns: None
        """
        self.scene.set_polygon_name(polygon_id, new_name)

    def set_process_task(self, parallel_task: callable, then_task: callable, parallel_task_args=None,
                         then_task_args=None) -> None:
        """
        Creates a new process with the given tasks and start it.

        Args:
            parallel_task: Task to execute in another process.
            then_task: Task to execute after the process. (the return object from the parallel task will be passed as
                       first parameter to this function)
            parallel_task_args: Arguments to give to the parallel task.
            then_task_args: Arguments to give to the then task.

        Returns: None
        """
        if parallel_task_args is None:
            parallel_task_args = []
        if then_task_args is None:
            then_task_args = []

        self.__process_manager.create_parallel_process(parallel_task,
                                                       parallel_task_args,
                                                       then_task,
                                                       then_task_args)

    def set_program_loading(self, new_state: bool = True) -> None:
        """
        Tell the program to set the loading state.

        Returns: None

        Args:
            new_state: Boolean indicating the state of the program (if it is loading or not)
        """
        self.program.set_loading(new_state)

    def set_task_for_next_frame(self, task: callable, n_frames: int = 2) -> None:
        """
        Add a task to do in the next frame.

        Args:
            n_frames: Number of frames to wait.
            task: Callable to call in the next frame.

        Returns: None
        """
        log.debug("Setting task for next frame")
        self.__pending_task_list.append({
            'task': task,
            'frames': n_frames  # need to be 2 to really wait one full frame
        })

    def set_task_with_loading_frame(self, task: callable, n_frames_to_wait: int = 3) -> None:
        """
        Set a task to be executed at the end of the next frame. Also configures the loading setting of
        the program to show the loading frame on the screen.

        Args:
            n_frames_to_wait: Number of frames to wait before executing the task.
            task: Task to be called in while showing a loading frame.

        Returns: None
        """
        self.program.set_loading(True)

        # noinspection PyMissingOrEmptyDocstring
        def task_loading():
            task()
            self.program.set_loading(False)

        self.set_task_for_next_frame(task_loading, n_frames_to_wait)

    def set_thread_task(self, parallel_task, then, parallel_task_args=None, then_task_args=None) -> None:
        """
        Add and start a new thread with the current task. At the end of the thread, the then
        function is called.

        If the parallel task return something other than None, then the object returned is given as the first
        parameter to the then task.

        Args:
            then_task_args: List of argument to use in the then task
            parallel_task_args: List of argument to use in the parallel task
            parallel_task: Task to be executed in parallel
            then: Task to be executed in the main thread after the parallel task

        Returns: None
        """
        self.__thread_manager.set_thread_task(parallel_task, then, parallel_task_args, then_task_args)

    def transform_points(self,
                         polygon_id: str,
                         model_id: str,
                         min_height: float,
                         max_height: float,
                         transformation_type: str = 'linear') -> None:
        """
        Ask the scene to interpolate the points of the specified polygon using a linear interpolation.

        Args:
            transformation_type: Type of transformation to do.
            model_id: ID of the model to use for the interpolation.
            polygon_id: ID of the polygon to use.
            min_height: Min height of the points once converted.
            max_height: Max height of the points once converted.

        Returns: None
        """
        try:
            self.scene.transform_points(polygon_id, model_id, min_height, max_height, transformation_type)

        except ModelTransformationError as e:
            if e.code == 4:
                self.set_modal_text('Error',
                                    'The current model is not supported to use to update the '
                                    'height of the vertices, try using another type of '
                                    'model.')
            elif e.code == 2:
                self.set_modal_text('Error',
                                    'The polygon must have at least 3 points to be able to '
                                    'modify the heights.')
            elif e.code == 3:
                self.set_modal_text('Error',
                                    'The polygon is not planar. Try using a planar polygon.')

    def undo_action(self) -> None:
        """
        Undo the most recent action made in the program.

        It is dependant of the active tool being used in the program.

        Returns: None
        """
        active_tool = self.get_active_tool()

        if active_tool == 'create_polygon':
            # remove the last point from the active polygon if there is an active polygon.
            log.debug('Undoing actions for tool create_polygon.')

            # ask for the active polygon and call the scene to remove the points
            if self.get_active_polygon_id() is not None:
                self.scene.remove_last_point_from_active_polygon()
            else:
                log.debug('Active polygon is None. Nothing to undo.')

        else:
            log.debug(f'Tool {active_tool} has no undo action defined.')

    def update_scene_models_colors(self):
        """
        Update the colors of the models in the scene with the colors that are
        in the ctp file stored in the program.

        Returns: None
        """
        self.scene.update_models_colors()

    def update_scene_values(self) -> None:
        """
        Update the configuration values related to the scene.
        Returns: None
        """
        Settings.update_scene_values()

    def update_scene_viewport(self) -> None:
        """
        Update the scene viewport with the new values that exist in the Settings.
        """
        self.scene.update_viewport()

    def get_program_view_mode(self) -> str:
        """
        Ask the program for the view mode being used.

        Returns: view mode being used by the program.
        """
        return self.program.get_view_mode()

    def set_program_view_mode(self, mode: str = '2D') -> None:
        """
        Set the program view mode to the selected mode.

        Raise ValueError if the mode is an invalid value.

        Args:
            mode: New mode to change to.

        Returns: None
        """
        if mode == '2D':
            self.program.set_view_mode_2D()
        elif mode == '3D':
            self.program.set_view_mode_3D()
        else:
            raise ValueError(f'Can not change program view mode to {mode}.')

    def modify_camera_radius(self, distance: float) -> None:
        """
        Ask the scene to get the camera closer to the model.

        Args:
            distance: Distance to get the camera closer.

        Returns: None
        """
        self.scene.modify_camera_radius(distance)

    def change_camera_elevation(self, angle) -> None:
        """
        Ask the scene to change the camera elevation.

        Args:
            angle: Angle to add to the elevation of the camera.

        Returns: None
        """
        self.scene.change_camera_elevation(angle)

    def change_camera_xy_angle(self, angle) -> None:
        """
        Ask the scene to change the azimuthal angle of the camera.

        Args:
            angle: angle to add to the angle of the camera.

        Returns: None
        """
        self.scene.change_camera_azimuthal_angle(angle)

    def move_camera_position(self, movement: tuple) -> None:
        """
        Ask the scene to move the camera position the given movement.

        Args:
            movement: offset to add to the position of the camera. Tuple must have 3 values.

        Returns: None
        """
        self.scene.move_camera(movement)
