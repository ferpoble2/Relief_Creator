"""
File that contain the Scene class. This class is in charge of the management of the models of the scene.
"""
import OpenGL.GL as GL
import OpenGL.constant as OGLConstant

from src.engine.scene.model.map2dmodel import Map2DModel
from src.engine.scene.model.polygon import Polygon
from src.engine.scene.model.model import Model
from src.input.NetCDF import read_info
from src.utils import get_logger

log = get_logger(module="SCENE")


class Scene:

    def __init__(self):
        """
        Constructor of the class.
        """
        self.__model_list = []
        self.__3d_model_list = []
        self.__polygon_list = []
        self.__engine = None

        self.__width_viewport = None
        self.__height_viewport = None

        # auxiliary variables
        # -------------------
        self.__should_execute_then_reload = 0
        self.__should_execute_then_optimize_gpu_memory = 0

        self.__polygon_id_count = 0

    def add_model(self, model: Model) -> None:
        """
        Add a model to the list of models.
        Args:
            model: Model to add to the list

        Returns: None
        """
        self.__model_list.append(model)

    def add_polygon(self, polygon: 'Polygon') -> None:
        """
        Add a new polygon to render on the scene.

        Args:
            polygon: Polygon to add to the scene

        Returns: None
        """
        log.debug("Added polygon to the scene")
        self.__polygon_list.append(polygon)
        self.__polygon_id_count += 1

    def add_vertex_to_active_polygon(self, position_x: int, position_y: int) -> None:
        """
        Add a new vertex to the active polygon on the screen.

        Args:
            position_x: Position x of the point in window coordinates
            position_y: Position y of the point in window coordinates (from top to bottom)

        Returns: None
        """
        active_polygon = self.__engine.get_active_polygon_id()

        # Raise exception when there is no active polygon.
        if active_polygon is None:
            raise AssertionError('There is no active polygon.')

        for polygon in self.__polygon_list:
            if polygon.get_id() == active_polygon:
                new_x, new_y = self.calculate_map_position_from_window(position_x, position_y)
                polygon.add_point(new_x, new_y)

    def calculate_map_position_from_window(self, position_x, position_y) -> (float, float):
        """
        Calculate the position of a point on the map currently being showed on the screen.

        Args:
            position_x: Window position x of the point
            position_y: Window position y (from top to bottom) of the point

        Returns: position_x, position_y of the new point in the map coordinates.
        """

        scene_settings = self.__engine.get_scene_setting_data()
        map_positions = self.get_active_model_showed_limits()
        window_settings = self.__engine.get_window_setting_data()

        x_dist_pixel = position_x - scene_settings['SCENE_BEGIN_X']
        y_dist_pixel = (window_settings['HEIGHT'] - position_y) - scene_settings['SCENE_BEGIN_Y']

        x_pos = map_positions['left'] + (map_positions['right'] - map_positions['left']) * x_dist_pixel / \
                scene_settings['SCENE_WIDTH_X']
        y_pos = map_positions['bottom'] + (map_positions['top'] - map_positions['bottom']) * y_dist_pixel / \
                scene_settings['SCENE_HEIGHT_Y']

        log.debug(f'Calculated position is: {x_pos} {y_pos}')
        return x_pos, y_pos

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
        for polygon in self.__polygon_list:
            if polygon.get_id() == polygon_id:
                polygon.set_line_color(color)

    def create_new_polygon(self) -> str:
        """
        Create a new polygon and adds it to the list of polygons.

        Returns: id of the created polygon
        """
        new_poligon_id = f"Polygon {self.__polygon_id_count}"
        polygon = Polygon(self, new_poligon_id)
        self.add_polygon(polygon)
        return new_poligon_id

    def delete_polygon_by_id(self, polygon_id: str) -> None:
        """
        Delete the polygon with the specified id from the scene

        Args:
            polygon_id: Id to use to delete.

        Returns: None
        """
        for polygon in self.__polygon_list:
            if polygon.get_id() == polygon_id:
                self.__polygon_list.remove(polygon)
                break

    def draw(self) -> None:
        """
        Draw the models in the list.

        Draw the models in the order of the list.
        Returns: None
        """
        for model in self.__model_list:
            model.draw()
        for polygon in self.__polygon_list:
            polygon.draw()

    def get_active_model_projection_matrix(self) -> 'np.array':
        """
        Get the projection matrix from the active model.

        Returns: array with the projection matrix of the active model.
        """
        active_model_id = self.__engine.get_active_model_id()
        for model in self.__model_list:
            if model.id == active_model_id:
                return model.get_projection_matrix()

    def get_active_model_showed_limits(self) -> dict:
        """
        Get a dictionary with the limits of the coordinates being showed by the current model on the scene.

        Returns: Dictionary with the limits
        """
        active_model_id = self.__engine.get_active_model_id()
        if active_model_id is None:
            raise AssertionError("There is no active model.")

        for model in self.__model_list:
            if model.id == active_model_id:
                return model.get_showed_limits()

    def get_float_bytes(self) -> int:
        """
        Get the float bytes used in a float to render.
        Ask the engine for this information (that is stored in the settings).

        Returns: Number of bytes used for store float numbers.
        """
        return self.__engine.get_float_bytes()

    def get_polygon_list(self) -> list:
        """
        Return a list with the polygons being used in the program.

        Returns: list with polygons being used in the program.
        """
        return self.__polygon_list

    def get_render_settings(self) -> dict:
        """
        Return a dictionary with the settings related to the polygons.

        Returns: Dictionary with the settings related to the polygon
        """
        return self.__engine.get_render_settings()

    def get_scene_setting_data(self) -> dict:
        """
        Get the scene settings.

        Returns: None
        """
        return self.__engine.get_scene_setting_data()

    def get_zoom_level(self) -> float:
        """
        Get the zoom level used by the program.

        Returns:  Zoom level
        """
        return self.__engine.get_zoom_level()

    def initialize(self, engine: 'Engine') -> None:
        """
        Initialize the component in the engine.
        Args:
            engine: Engine to use

        Returns: None
        """
        self.__engine = engine

    def move_models(self, x_movement: int, y_movement: int) -> None:
        """
        Move the models on the scene.

        Args:
            x_movement: Movement in the x-axis
            y_movement: Movement in the y-axis

        Returns: None
        """
        log.debug("Moving models")
        for model in self.__model_list:
            model.move(x_movement, y_movement)

    def optimize_gpu_memory_async(self, then: callable) -> None:
        """
        Optimize the gpu memory of the models.

        Args:
            then: Routine executed after the parallel routine.

        Returns: None
        """
        log.debug("Optimizing gpu memory of models")
        self.__should_execute_then_optimize_gpu_memory = len(self.__model_list)

        def then_routine():
            self.__should_execute_then_optimize_gpu_memory -= 1
            self.__should_execute_then_optimize_gpu_memory = max(0, self.__should_execute_then_optimize_gpu_memory)

            if self.__should_execute_then_optimize_gpu_memory == 0:
                self.__should_execute_then_optimize_gpu_memory = len(self.__model_list)
                then()

        for model in self.__model_list:
            model.optimize_gpu_memory_async(then_routine)

        # if there is no models, call the then routine doing nothing
        if len(self.__model_list) == 0:
            then()

    def refresh_with_model_2d_async(self, path_color_file: str, path_model: str, model_id: str = 'main',
                                    then=lambda: None) -> 'Model':
        """
        Refresh the scene, removing all the models, and adding the new model specified
        in the input.

        The model added will be added as a 2d model to the program with the id 'main'.

        The model must  be in netCDF format.

        The color file must be in CTP format.

        Args:
            then: Function to be executed at the end of the async routine
            model_id: Model ID to use in the model added
            path_color_file: Path to the CTP file with the colors
            path_model: Path to the model to use in the application

        Returns: None

        """

        log.debug("Reading information from file.")
        X, Y, Z = read_info(path_model)

        log.debug("Generating model")
        model = Map2DModel(self)

        def then_routine():
            log.debug("Settings colors from file.")
            model.set_color_file(path_color_file)
            model.calculate_projection_matrix(self.__engine.get_scene_setting_data())
            model.wireframes = False
            model.id = model_id

            self.remove_all_models()
            self.add_model(model)

            self.__engine.reset_zoom_level()

            # call the then routine
            then()

        log.debug("Setting vertices from grid.")
        model.set_vertices_from_grid_async(X, Y, Z, self.__engine.get_quality(), then_routine)

    def reload_models_async(self, then):
        """
        Ask the 2D models to reload with the new resolution of the screen.

        Returns: None

        Args:
            then: Function to be called after all the async routine.
        """

        # set up the then routine that should executes only once.
        # -------------------------------------------------------
        self.__should_execute_then_reload = len(self.__model_list)

        def then_routine():
            self.__should_execute_then_reload -= 1
            self.__should_execute_then_reload = max(self.__should_execute_then_reload, 0)

            if self.__should_execute_then_reload == 0:
                self.__should_execute_then_reload = len(self.__model_list)
                then()

        for model in self.__model_list:
            model.recalculate_vertices_from_grid_async(quality=self.__engine.get_quality(), then=then_routine)

        # if there is no models, call the then routine doing nothing
        if len(self.__model_list) == 0:
            then()

    def remove_all_models(self) -> None:
        """
        Remove all models from the list of models.
        Returns: None
        """
        self.__model_list = []

    def remove_model(self, id_model: str) -> None:
        """
        Return the model with the specified id.
        Args:
            id_model: Id of the model to remove.

        Returns: None
        """
        model_to_remove = None
        for model in self.__model_list:
            if model.id == id_model:
                model_to_remove = model

        self.__model_list.remove(model_to_remove)

    def set_loading_message(self, new_msg: str) -> None:
        """
        Change the loading message shown in the loading frame.

        Args:
            new_msg: New message to show

        Returns: None
        """
        self.__engine.set_loading_message(new_msg)

    def set_map_position(self, new_position: list) -> None:
        """
        Tell the engine the new position of the map.

        Args:
            new_position: New position to use.

        Returns: None
        """
        self.__engine.set_map_position(new_position)

    def set_parallel_task(self, parallel_task, then):
        """
        Set a parallel task in the engine.

        Args:
            parallel_task: Task to execute in parallel
            then: Task to execute after the parallel task

        Returns: None
        """
        self.__engine.set_thread_task(parallel_task, then)

    def set_polygon_mode(self, polygon_mode: OGLConstant.IntConstant) -> None:
        """
        Select if the models uses the wireframe mode or not.
        Args:
            polygon_mode: OpenGL polygon mode to draw the model.

        Returns: None
        """
        for model in self.__model_list:
            model.polygon_mode = polygon_mode

    def update_models_colors(self) -> None:
        """
        Update the colors of the models reloading the colors from the file used in the program.

        Returns: None
        """
        color_file = self.__engine.get_CPT_file()
        for model in self.__model_list:
            model.set_color_file(color_file)

    def update_models_projection_matrix(self) -> None:
        """
        Update the projection matrix of the models.

        Returns: None
        """
        log.debug("Updating projection matrix of models.")
        scene_data = self.__engine.get_scene_setting_data()

        for model in self.__model_list:
            model.calculate_projection_matrix(scene_data, self.__engine.get_zoom_level())

    def update_viewport(self) -> None:
        """
        Update the viewport with the new values that exist in the Settings.
        """
        log.debug("Updating viewport")
        self.update_viewport_variables()

        scene_data = self.__engine.get_scene_setting_data()
        GL.glViewport(scene_data['SCENE_BEGIN_X'], scene_data['SCENE_BEGIN_Y'], scene_data['SCENE_WIDTH_X'],
                      scene_data['SCENE_HEIGHT_Y'])

        self.update_models_projection_matrix()

    def update_viewport_variables(self):
        """
        Update the viewport variables.

        Returns: None
        """
        viewport_data = self.__engine.get_scene_setting_data()
        self.__width_viewport = viewport_data['SCENE_WIDTH_X']
        self.__height_viewport = viewport_data['SCENE_HEIGHT_Y']
