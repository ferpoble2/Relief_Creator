"""
File that contain the Scene class. This class is in charge of the management of the models of the scene.
"""
from typing import Dict, List
from src.type_hinting import *

import OpenGL.GL as GL
import numpy as np

# noinspection PyPep8Naming
import OpenGL.constant as OGLConstant

from src.engine.scene.model.map2dmodel import Map2DModel
from src.engine.scene.model.map3dmodel import Map3DModel
from src.engine.scene.model.polygon import Polygon
from src.engine.scene.model.plane import Plane
from src.engine.scene.model.model import Model
from src.engine.scene.model.lines import Lines
from src.utils import get_logger
from src.engine.scene.transformation_helper import TransformationHelper
from src.engine.scene.camera import Camera

# TODO: this should be just another code in SceneError
from src.error.non_existent_polygon_error import NonExistentPolygonError

from src.error.model_transformation_error import ModelTransformationError
from src.error.scene_error import SceneError
from src.error.interpolation_error import InterpolationError

log = get_logger(module="SCENE")


class Scene:
    """
    Class in charge of all the elements that are rendered using Opengl.

    This class manage all the configurations needed to show the models in the screen and the different operations
    that they do.
    """

    def __init__(self, engine: 'Engine' = None):
        """
        Constructor of the class.
        """
        self.__model_hash: Dict[str, 'Map2DModel'] = {}
        self.__3d_model_hash: Dict[str, 'Map3DModel'] = {}
        self.__polygon_hash: Dict[str, 'Polygon'] = {}
        self.__interpolation_area_hash: Dict[str, List['Model']] = {}
        self.__engine: 'Engine' = engine

        self.__width_viewport = 0
        self.__height_viewport = 0

        self.__camera = Camera()

        # auxiliary variables
        # -------------------

        # variable that indicated witch function then to use when there is
        # more than one model on the scene.
        self.__should_execute_then_reload = 0
        self.__should_execute_then_optimize_gpu_memory = 0

        self.__polygon_id_count = 0
        self.__model_id_count = 0

    def __process_filters(self, filters=None):
        """
        Given a list with the filters in the format [(id_filter, args),...], get the data and format them in a
        format suitable for the use in the TransformationHelper.

        The list of accepted filters and its arguments are as follows:
            height_less_than: int
            height_greater_than: int
            is_in: str
            is_not_in: str

        The expected value on the filters is_is and is_not_in is the id of a polygon.

        Args:
            filters: Filters to use.

        Returns: List with the filters and the data necessary to apply them.
        """

        if filters is None:
            filters = []

        filter_data = []
        for filter_obj in filters:
            id_filter = filter_obj[0]

            # height filters
            if id_filter == 'height_less_than' or id_filter == 'height_greater_than':
                height = float(filter_obj[1])
                filter_data.append((id_filter, height))

            # polygon filters
            elif id_filter == 'is_in' or id_filter == 'is_not_in':
                # get the points of the polygon
                polygon_id = filter_obj[1]

                # get the points of the polygon, raise and exception if it there is problems in the
                # retrieve of the information
                try:
                    polygon_points = self.get_polygon_points(polygon_id)
                except SceneError:  # polygon not found
                    raise ModelTransformationError(6)

                # store the data
                filter_data.append((id_filter, polygon_points))
            else:
                raise NotImplementedError(f'Processing process for filter {id_filter} not implemented on the Scene.')

        return filter_data

    def __transform_points_using_linear_transformation(self,
                                                       polygon_id: str,
                                                       model_id: str,
                                                       min_height: float,
                                                       max_height: float,
                                                       filters: list = None) -> None:
        """
        Method that transform the points of the model using the linear transformation and applies all the
        filter that were passed to it.

        Args:
            polygon_id: ID of the polygon to use for the transformation.
            model_id: ID of the model to use.
            min_height: min height to use for the interpolation.
            max_height: max height to use for the interpolation.
            filters: List with the filters to use in the modification of the points. List must be in the
                format [(filter_id, args),...]

        Returns: None
        """

        if filters is None:
            filters = []

        # GET THE DATA FOR THE TRANSFORMATION AND CHECK VALIDITY
        # ------------------------------------------------------

        # Get the model to use and the polygon to use for the transformation.
        model = self.__model_hash[model_id]
        polygon = self.__polygon_hash[polygon_id]

        # ask the model and polygon for the parameters to calculate the new height
        vertices_shape = model.get_vertices_shape()
        vertex_array = model.get_vertices_array().reshape(vertices_shape)
        height_array = model.get_height_array().reshape((vertices_shape[0], vertices_shape[1]))
        polygon_points = polygon.get_point_list()

        if len(polygon_points) < 9:
            raise ModelTransformationError(2)

        if not polygon.is_planar():
            raise ModelTransformationError(3)

        # process the filter data to apply the transformations.
        filter_data = self.__process_filters(filters)

        # CALL THE THREAD TASK
        # --------------------

        # define mutable object to store results to use from the parallel task to the then task
        new_height = [None]

        # noinspection PyMissingOrEmptyDocstring,PyShadowingNames,PyUnresolvedReferences
        def parallel_task(new_height: list, vertex_array: 'numpy.array', height_array: 'numpy.array',
                          polygon_points: list, max_height: float, min_height: float, filter_data: list):
            # calculate the new height of the points
            new_height[0] = TransformationHelper().modify_points_inside_polygon_linear(vertex_array,
                                                                                       height_array,
                                                                                       polygon_points,
                                                                                       max_height,
                                                                                       min_height,
                                                                                       filter_data)

        # noinspection PyMissingOrEmptyDocstring,PyShadowingNames,PyUnresolvedReferences
        def then(new_height: list, engine: 'Engine', model: Map2DModel):
            # tell the polygon the new height of the vertices
            model.set_height_buffer(new_height[0])
            engine.set_program_loading(False)

        # define the parallel functions to use
        self.__engine.set_loading_message('Changing height...')
        self.__engine.set_program_loading(True)
        self.__engine.set_thread_task(parallel_task, then,
                                      parallel_task_args=[new_height,
                                                          vertex_array,
                                                          height_array,
                                                          polygon_points,
                                                          max_height,
                                                          min_height,
                                                          filter_data],
                                      then_task_args=[new_height,
                                                      self.__engine,
                                                      model])

    def add_model(self, model: Map2DModel) -> None:
        """
        Add a model to the hash of models.
        Args:
            model: Model to add to the hashtable.

        Returns: None
        """
        self.__model_hash[model.id] = model

    def add_new_vertex_to_active_polygon_using_real_coords(self, x_coord: float, y_coord: float) -> None:
        """
        Add a new point to the active polygon using real coordinates.

        Args:
            x_coord: x coordinate of the new point
            y_coord: y coordinate of the new point

        Returns: None
        """
        active_polygon = self.__engine.get_active_polygon_id()
        if active_polygon in self.__polygon_hash:
            self.__polygon_hash[active_polygon].add_point(x_coord, y_coord)

    def add_new_vertex_to_active_polygon_using_window_coords(self, position_x: int, position_y: int) -> None:
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

        if active_polygon in self.__polygon_hash:
            new_x, new_y = self.calculate_map_position_from_window(position_x, position_y)
            self.__polygon_hash[active_polygon].add_point(new_x, new_y)

    def add_polygon(self, polygon: 'Polygon') -> None:
        """
        Add a new polygon to render on the scene.

        Args:
            polygon: Polygon to add to the scene

        Returns: None
        """
        log.debug("Added polygon to the scene")
        self.__polygon_hash[polygon.get_id()] = polygon
        self.__polygon_id_count += 1

    def apply_smoothing_algorithm(self, polygon_id, model_id, distance_to_polygon) -> None:
        """
        Apply a smoothing algorithm over in the area between the polygon and the external polygon generated
        using the distance specified.

        Args:
            polygon_id: id of the polygon to use.
            model_id: id of the model to use.
            distance_to_polygon: distance to use to calculate the external polygon.

        Returns: None
        """
        polygon = self.__polygon_hash[polygon_id]
        model = self.__model_hash[model_id]

        polygon_points = polygon.get_point_list()
        external_polygon_points = polygon.get_exterior_polygon_points(distance_to_polygon)

        vertices_shape = model.get_vertices_shape()

        vertices_model = model.get_vertices_array()
        vertices_model = vertices_model.reshape(vertices_shape)

        heights_model = model.get_height_array()
        heights_model = heights_model.reshape(vertices_shape[0:2])

        new_heights = TransformationHelper().apply_smoothing_over_area(polygon_points,
                                                                       external_polygon_points,
                                                                       vertices_model,
                                                                       heights_model)

        model.set_height_buffer(new_heights)

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

        scene_x = scene_settings['SCENE_WIDTH_X']
        scene_y = scene_settings['SCENE_HEIGHT_Y']

        x_pos = map_positions['left'] + (map_positions['right'] - map_positions['left']) * x_dist_pixel / scene_x
        y_pos = map_positions['bottom'] + (map_positions['top'] - map_positions['bottom']) * y_dist_pixel / scene_y

        log.debug(f'Calculated position is: {x_pos} {y_pos}')
        return x_pos, y_pos

    def calculate_max_min_height(self, model_id: str, polygon_id: str) -> tuple:
        """
        Calculate the maximum and minimum height of the vertices that are inside the polygon.

        Args:
            model_id: ID of the model to use.
            polygon_id: ID of the polygon to use.

        Returns: Tuple with the maximum and minimum height of the vertices inside the polygon.
        """

        # get the important information.
        model = self.__model_hash[model_id]
        if not isinstance(model, Map2DModel):
            raise SceneError(3)

        polygon = self.__polygon_hash[polygon_id]

        # ask the model and polygon for the parameters to calculate the new height
        vertices_shape = model.get_vertices_shape()
        vertex_array = model.get_vertices_array().reshape(vertices_shape)
        height_array = model.get_height_array().reshape((vertices_shape[0], vertices_shape[1]))
        polygon_points = polygon.get_point_list()

        if len(polygon_points) < 9:
            raise SceneError(2)

        if not polygon.is_planar():
            raise SceneError(1)

        return TransformationHelper().get_max_min_inside_polygon(vertex_array, polygon_points, height_array)

    def change_camera_azimuthal_angle(self, angle):
        """
        Change the camera azimuthal angle

        Args:
            angle: Angle to add to the azimuthal angle.

        Returns: None
        """
        self.__camera.modify_azimuthal_angle(angle)

    def change_camera_elevation(self, angle):
        """
        Change the camera angle elevation.

        Args:
            angle: Angle to add to the elevation of the camera.

        Returns: None
        """
        self.__camera.modify_elevation(angle)

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
        if polygon_id in self.__polygon_hash:
            self.__polygon_hash[polygon_id].set_line_color(color)

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
        if polygon_id in self.__polygon_hash:
            self.__polygon_hash[polygon_id].set_dot_color(color)

    def change_height_unit_3D_model(self, model_id: str, measure_unit: str) -> None:
        """
        Change the measure unit used for the height of the model.

        This has an effect in the factor used to calculate the height at the moment of the rendering in 3D.

        Args:
            model_id: ID of the model to modify.
            measure_unit: New unit to use. Values can be ['meters', 'kilometers']

        Returns: None
        """
        self.__3d_model_hash[model_id].change_height_measure_unit(measure_unit)

    def change_map_unit_3D_model(self, model_id: str, measure_unit: str) -> None:
        """
        Change the measure unit used for the position of the points on the model.

        Args:
            model_id: id of the model to modify the measure unit.
            measure_unit: new measure unit to use.

        Returns: None
        """
        self.__3d_model_hash[model_id].change_vertices_measure_unit(measure_unit)

    def change_normalization_height_factor(self, active_model: str, new_factor: float) -> None:
        """
        Change the height normalization factor of the specified model.

        Args:
            active_model: ID of the 3D model to change the height normalization factor.
            new_factor: New factor to use in the model.

        Returns: None
        """
        self.__3d_model_hash[active_model].change_height_normalization_factor(new_factor)

    # noinspection SpellCheckingInspection
    def create_and_add_map3Dmodel(self, model_id: str, model_2d: Map2DModel) -> None:
        """
        Create a new map3Dmodel object and add it to the scene.

        Returns: Id of the new map3Dmodel

        Args:
            model_id: Id of the model.
            model_2d: Model 2D from wich extract the data to use to see the model in 3D.
        """

        # noinspection PyMissingOrEmptyDocstring
        def task_loading():
            self.reset_camera_values()
            new_model = Map3DModel(self, model_2d)
            new_model.id = model_id

            # add the model to the hash
            self.__3d_model_hash[model_id] = new_model

        self.__engine.set_loading_message('Generating 3D model...')
        self.__engine.set_task_with_loading_frame(task_loading, 2)

    def create_new_polygon(self) -> str:
        """
        Create a new polygon and adds it to the list of polygons.

        Returns: id of the created polygon
        """

        # generate a new id for the polygon
        new_polygon_id = f"Polygon {self.__polygon_id_count}"

        # create the polygon and return its id
        polygon = Polygon(self, new_polygon_id)
        self.add_polygon(polygon)
        return new_polygon_id

    def delete_polygon_by_id(self, polygon_id: str) -> None:
        """
        Delete the polygon with the specified id from the scene.

        Args:
            polygon_id: Id to use to delete.

        Returns: None
        """
        if polygon_id in self.__polygon_hash:
            self.__polygon_hash.pop(polygon_id)

            # delete the interpolation area if they have
            if polygon_id in self.__interpolation_area_hash:
                self.__interpolation_area_hash.pop(polygon_id)

    def delete_polygon_param(self, polygon_id: str, key: str) -> None:
        """
        Delete a parameter from the polygon.

        Args:
            polygon_id: ID of the polygon.
            key: Key to be deleted.

        Returns: None
        """
        try:
            self.__polygon_hash[polygon_id].delete_parameter(key)
        except KeyError:
            # noinspection PyTypeChecker
            raise NonExistentPolygonError(f'Polygon {polygon_id} does not exist in the program')

    def draw(self) -> None:
        """
        Draw the models in the hash of models.

        Draw the models in the order of the list.
        Returns: None
        """

        # get the active model
        active_model = self.__engine.get_active_model_id()

        # check if draw the 2D or the 3D of the models.
        if self.__engine.get_program_view_mode() == '2D':
            if active_model is not None:
                self.__model_hash[active_model].draw()
            for area_models in self.__interpolation_area_hash.values():
                for model in area_models:
                    model.draw()
            for polygon in self.__polygon_hash.values():
                polygon.draw()
        elif self.__engine.get_program_view_mode() == '3D':
            if active_model in self.__3d_model_hash:
                self.__3d_model_hash[active_model].draw()
            else:
                self.create_and_add_map3Dmodel(active_model,
                                               self.__model_hash[active_model])

    # noinspection PyUnresolvedReferences
    def get_active_model_projection_matrix(self) -> np.array:
        """
        Get the projection matrix from the active model.

        Returns: array with the projection matrix of the active model.
        """
        active_model_id = self.__engine.get_active_model_id()
        if active_model_id in self.__model_hash:
            return self.__model_hash[active_model_id].get_projection_matrix()

    def get_active_model_showed_limits(self) -> dict:
        """
        Get a dictionary with the limits of the coordinates being showed by the current model on the scene.

        Returns: Dictionary with the limits
        """
        active_model_id = self.__engine.get_active_model_id()
        if active_model_id is None:
            raise AssertionError("There is no active model.")

        if active_model_id in self.__model_hash:
            return self.__model_hash[active_model_id].get_showed_limits()

    def get_active_polygon_id(self) -> str:
        """
                Get the id of the active polygon on the program.

                Returns: the id of the active polygon.
                """
        return self.__engine.get_active_polygon_id()

    def get_camera_data(self) -> dict:
        """
        Get and returns the data related to the camera.

        Returns: dictionary with the data being used used by the camera.
        """

        return {
            'position': self.__camera.get_camera_offset_position(),
            'azimuthal': self.__camera.get_azimuthal_grades(),
            'elevation': self.__camera.get_elevation_grades(),
            'radius': self.__camera.get_radius()
        }

    def get_camera_settings(self) -> dict:
        """
        Ask the engine for the settings related to the camera.

        Returns: Dictionary with the settings related to the camera.
        """
        return self.__engine.get_camera_settings()

    def get_camera_view_matrix(self) -> np.ndarray:
        """
        Get the view matrix generated by the camera.

        Returns: Matrix generated by the camera to use as a view matrix.
        """
        return self.__camera.get_view_matrix()

    def get_extra_reload_proportion_setting(self) -> float:
        """
        Ask the engine for the value of the extra reload proportion stored in the settings.

        Returns: Float with the value of the proportion to use.
        """
        return self.__engine.get_extra_reload_proportion_setting()

    def get_float_bytes(self) -> int:
        """
        Get the float bytes used in a float to render.
        Ask the engine for this information (that is stored in the settings).

        Returns: Number of bytes used for store float numbers.
        """
        return self.__engine.get_float_bytes()

    def get_height_normalization_factor(self, model_3d_id: str) -> float:
        """
        Get the height normalization factor of the 3d model specified.

        If model is not in the list of 3D models, then KeyError is raised.

        Args:
            model_3d_id: Id of the model too ask for the height normalization factor.

        Returns: Factor being used by the model.
        """
        model = self.__3d_model_hash[model_3d_id]
        return model.get_normalization_height_factor()

    # noinspection SpellCheckingInspection
    def get_map2dmodel_vertices_array(self, model_id: str) -> np.ndarray:
        """
        Get the array of vertices of the specified model.

        Id model is not map2dmodel then TypeError exception is raised.

        Args:
            model_id: ID of the model.

        Returns: Array with the vertices of the model.
        """
        model = self.__model_hash[model_id]
        if not isinstance(model, Map2DModel):
            raise TypeError(f'Model {model_id} is not a Map2DModel instance.')

        vertices_array = model.get_vertices_array().reshape(model.get_vertices_shape())
        heights = model.get_height_array().reshape((vertices_array.shape[0], vertices_array.shape[1]))

        vertices_array[:, :, 2] = heights
        return vertices_array

    def get_point_list_from_polygon(self, polygon_id: str) -> list:
        """
        Return the list of points from a given polygon.

        Args:
            polygon_id: ID of the polygon.

        Returns: List with the points of the polygon.
        """
        try:
            return self.__polygon_hash[polygon_id].get_point_list()
        except KeyError:
            # noinspection PyTypeChecker
            raise NonExistentPolygonError(f"Polygon with ID {polygon_id} does not exist.")

    def get_polygon_id_list(self) -> list:
        """
        Return a list with the ids of the polygons being used in the program.

        Returns: list with polygon ids being used in the program.
        """
        return list(self.__polygon_hash.keys())

    def get_polygon_name(self, polygon_id: str) -> str:
        """
        Get the name of a polygon given its id

        Args:
            polygon_id: Id of the polygon

        Returns: Name of the polygon
        """
        if polygon_id in self.__polygon_hash:
            return self.__polygon_hash[polygon_id].get_name()

    def get_polygon_params(self, polygon_id: str) -> list:
        """
        Get the parameters of certain polygon.

        Args:
            polygon_id: ID of the polygon.

        Returns: List with the parameters of the polygon.
        """
        try:
            return self.__polygon_hash[polygon_id].get_parameter_list()
        except KeyError:
            # noinspection PyTypeChecker
            raise NonExistentPolygonError(f'Polygon {polygon_id} does not exist in the program')

    def get_polygon_points(self, polygon_id: str) -> list:
        """
        Return the list of points of a polygon.

        Args:
            polygon_id: ID of the polygon.

        Returns: List with the points of the polygon.
        """
        try:
            return self.__polygon_hash[polygon_id].get_point_list()

        except KeyError:
            raise SceneError(5)

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

    def interpolate_points(self, polygon_id: str, model_id: str, distance: float, type_interpolation: str) -> None:
        """
        Interpolate the points at the exterior of the polygon using a linear interpolation method.

        Args:
            type_interpolation: Type of interpolation to use.
            polygon_id: ID of the polygon to use.
            model_id: ID of the model to use.
            distance: Distance to use for the interpolation.

        Returns: None
        """

        # get the data necessary for the interpolation
        polygon = self.__polygon_hash[polygon_id]
        model = self.__model_hash[model_id]

        # check for errors
        # ----------------
        if len(polygon.get_point_list()) < 9:
            raise InterpolationError(1)

        if distance <= 0:
            raise InterpolationError(2)

        if not isinstance(model, Map2DModel):
            raise InterpolationError(3)

        # get the points to modify
        vertices_shape = model.get_vertices_shape()
        vertices = model.get_vertices_array().reshape(vertices_shape)
        height = model.get_height_array().reshape((vertices_shape[0], vertices_shape[1]))
        polygon_points = polygon.get_point_list()
        external_polygon_points = polygon.get_exterior_polygon_points(distance)

        # noinspection PyShadowingNames
        def parallel_task(vertices, polygon_points, height, external_polygon_points, type_interpolation):
            """
            Task to run in parallel in a different thread.

            Args:
                vertices: Vertices to use to interpolate.
                polygon_points: List of points of the polygon.
                height: Array of heights.
                external_polygon_points: List of points of the external polygon..
                type_interpolation: Type of interpolation to use.
            """
            new_calculated_height = TransformationHelper().interpolate_points_external_to_polygon(
                vertices,
                polygon_points,
                height,
                external_polygon_points,
                type_interpolation)
            return new_calculated_height

        # noinspection PyShadowingNames
        def then_task(new_height, map2d_model, engine):
            """
            Task to execute after the parallel routine.

            Args:
                map2d_model: Model to change the heights.
                new_height: New heights.
                engine: Engine used in the program.
            """
            # save the changes to the model
            map2d_model.set_height_buffer(new_height)
            engine.set_program_loading(False)

        self.__engine.set_loading_message('Interpolating points, this may take a while.')
        self.__engine.set_program_loading(True)
        self.__engine.set_thread_task(parallel_task, then_task,
                                      (vertices, polygon_points, height, external_polygon_points, type_interpolation),
                                      (model, self.__engine))

    def is_polygon_planar(self, polygon_id: str) -> bool:
        """
        Check if the polygon is planar or not.

        Return None if polygon is not in the list of polygons.

        Args:
            polygon_id: Polygon id to check

        Returns: boolean indicating if the polygon is planar or not
        """
        if polygon_id in self.__polygon_hash:
            return self.__polygon_hash[polygon_id].is_planar()

    def load_preview_interpolation_area(self, distance: float, polygon_id: str, z_value: float = 0.5,
                                        generate_area: bool = False) -> None:
        """
        Calculate the interpolation area for the active polygon and draw it on the scene.

        WARNING: in case of generating the area, it can be time expensive and in some cases, inaccurate.

        Args:
            polygon_id: id of the polygon to load the interpolation area.
            generate_area: Generate the area of the interpolation.
            z_value: Value to use for the third component of the vertices in the area polygons.
            distance: Distance to use to calculate the external area.

        Returns: None
        """
        log.debug('Getting polygons...')
        polygon = self.__polygon_hash[polygon_id]
        polygon_points = polygon.get_point_list()

        if len(polygon_points) < 9:
            raise SceneError(2)

        polygon_external_points = polygon.get_exterior_polygon_points(distance)

        # noinspection PyMissingOrEmptyDocstring,PyShadowingNames,PyUnresolvedReferences
        def thread_task(polygon_points: list, polygon_external_points: list, distance: float, engine: 'Engine',
                        calculate_area: bool, z_value: float):
            engine.set_program_loading(True)
            engine.set_loading_message('Calculating interpolation area...')

            if calculate_area:
                log.debug('Get triangulation triangles...')
                triangulation = TransformationHelper().get_interpolation_zone_triangulation(polygon_points,
                                                                                            polygon_external_points,
                                                                                            distance,
                                                                                            z_value)

            else:
                triangulation = []

            return triangulation

        # noinspection PyMissingOrEmptyDocstring
        def then_task(triangulation: list, external_polygon_points: list, scene: 'Scene', calculate_area: bool):
            # NOTE: triangulation can be a void list

            log.debug('Generating Lines')
            lines_external = Lines(self)
            lines_external.set_line_color([1, 0, 0, 0.5])
            for ind in range(int(len(external_polygon_points) / 3)):

                point_1 = (external_polygon_points[ind * 3],
                           external_polygon_points[ind * 3 + 1],
                           external_polygon_points[ind * 3 + 2])

                if ind == len(external_polygon_points) / 3 - 1:
                    point_2 = (external_polygon_points[0],
                               external_polygon_points[1],
                               external_polygon_points[2])
                else:
                    point_2 = (external_polygon_points[ind * 3 + 3],
                               external_polygon_points[ind * 3 + 4],
                               external_polygon_points[ind * 3 + 5])

                lines_external.add_line(point_1, point_2)
            scene.__interpolation_area_hash[self.__engine.get_active_polygon_id()] = [lines_external]

            if calculate_area:
                area_model_external = Plane(self)
                area_model_external.set_triangles(np.array(triangulation))
                scene.__interpolation_area_hash[self.__engine.get_active_polygon_id()].append(area_model_external)

            scene.__engine.set_program_loading(False)

        self.__engine.set_thread_task(parallel_task=thread_task,
                                      then=then_task,
                                      parallel_task_args=(polygon_points,
                                                          polygon_external_points,
                                                          distance,
                                                          self.__engine,
                                                          generate_area,
                                                          z_value),
                                      then_task_args=(polygon_external_points, self, generate_area))

    def modify_camera_radius(self, distance: float) -> None:
        """
        Make the radius of the camera smaller.

        Args:
            distance: distance to add or subtract from the camera radius.

        Returns: None
        """
        self.__camera.modify_radius(distance)

    def move_camera(self, movement: tuple) -> None:
        """
        Move the camera the specified values given in the input.

        The movement moves the camera and also the point where it is looking at.

        Args:
            movement: Tuple of 3 values with the movement to do on the camera.

        Returns: None
        """
        self.__camera.modify_camera_offset(movement)

    def move_models(self, x_movement: int, y_movement: int) -> None:
        """
        Move the models on the scene.

        Args:
            x_movement: Movement in the x-axis
            y_movement: Movement in the y-axis

        Returns: None
        """
        log.debug("Moving models")
        for model in self.__model_hash.values():
            model.move(x_movement, y_movement)

    def optimize_gpu_memory_async(self, then: callable) -> None:
        """
        Optimize the gpu memory of the models.

        Args:
            then: Routine executed after the parallel routine.

        Returns: None
        """
        log.debug("Optimizing gpu memory of models")
        self.__should_execute_then_optimize_gpu_memory = len(self.__model_hash)

        # noinspection PyMissingOrEmptyDocstring
        def then_routine():
            self.__should_execute_then_optimize_gpu_memory -= 1
            self.__should_execute_then_optimize_gpu_memory = max(0, self.__should_execute_then_optimize_gpu_memory)

            if self.__should_execute_then_optimize_gpu_memory == 0:
                self.__should_execute_then_optimize_gpu_memory = len(self.__model_hash)
                then()

        for model in self.__model_hash.values():
            model.optimize_gpu_memory_async(then_routine)

        # if there is no models, call the then routine doing nothing
        if len(self.__model_hash) == 0:
            then()

    def refresh_with_model_2d_async(self, path_color_file: str, path_model: str, then=lambda x: None) -> None:
        """
        Refresh the scene, removing all the models, and adding the new model specified
        in the input.

        The model added will be added as a 2d model to the program with the id 'main'.

        The model must  be in netCDF format.

        The color file must be in CTP format.

        The 'then' parameter is the logic that will be executed after the process finish loading the model into memory.
        This parameter is a function that must receive one parameter and will be called with the model id as the
        value for that parameter.

        Args:
            then: Function to be executed at the end of the async routine. Must receive one parameter (the model id).
            path_color_file: Path to the CTP file with the colors
            path_model: Path to the model to use in the application

        Returns: None

        """

        log.debug("Reading information from file.")
        X, Y, Z = self.__engine.read_netcdf_info(path_model)

        log.debug("Generating model")
        model = Map2DModel(self)

        # noinspection PyMissingOrEmptyDocstring
        def then_routine():
            log.debug("Settings colors from file.")
            model.set_color_file(path_color_file)
            model.calculate_projection_matrix(self.__engine.get_scene_setting_data())
            model.wireframes = False

            # even if the model is not in the program anymore, we do not want repeated ids.
            model.id = self.__model_id_count
            self.__model_id_count += 1

            # this line have to be removed for the program to accept more than one model at the same time
            self.remove_all_models()
            self.add_model(model)

            self.__engine.reset_zoom_level()

            # call the then routine
            then(model.id)

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
        self.__should_execute_then_reload = len(self.__model_hash)

        def then_routine():
            """
            Method that lower the value of the parameter __should_execute_then_reload by one every time that a
            model finished the method recalculate_vertices_from_grid_async.

            This method is executed so that the THEN method given to the reload_models_async method only runs when all
            the models finished the execution of their threads.

            Returns: None
            """
            self.__should_execute_then_reload -= 1
            self.__should_execute_then_reload = max(self.__should_execute_then_reload, 0)

            if self.__should_execute_then_reload == 0:
                self.__should_execute_then_reload = len(self.__model_hash)
                then()

        for model in self.__model_hash.values():
            model.recalculate_vertices_from_grid_async(quality=self.__engine.get_quality(), then=then_routine)

        # if there is no models, call the then routine doing nothing
        if len(self.__model_hash) == 0:
            then()

    def remove_all_models(self) -> None:
        """
        Remove all models from the hash of models.
        Returns: None
        """
        self.__model_hash = {}

    def remove_interpolation_preview(self, polygon_id: str) -> None:
        """
        Remove the interpolation area of the specified polygon.

        Do nothing if the area does not exists.

        Args:
            polygon_id: Polygon to remove the area to.

        Returns: None
        """
        self.__interpolation_area_hash.pop(polygon_id, None)

    def remove_last_point_from_active_polygon(self) -> None:
        """
        Remove the last point added from the active polygon.

        Raise error if there is not active polygon.
        Raise error if active polygon is not in the list of the scene.

        Returns: None
        """
        polygon_id = self.__engine.get_active_polygon_id()

        if polygon_id is None:
            raise AssertionError('There is no active polygon.')

        log.debug(f'Removing last point from polygon {polygon_id}')
        if polygon_id in self.__polygon_hash:
            self.__polygon_hash[polygon_id].remove_last_added_point()
            return

        raise AssertionError('Active polygon is not in the list of polygons')

    def remove_model(self, id_model: str) -> None:
        """
        Delete the model with the specified id.

        Args:
            id_model: Id of the model to remove.

        Returns: None
        """

        if id_model in self.__model_hash:
            self.__model_hash.pop(id_model)

    def reset_camera_values(self) -> None:
        """
        Reset the camera values to the initial ones.

        Returns: None
        """
        self.__camera.reset_values()

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

    def set_modal_text(self, title_modal: str, msg: str) -> None:
        """
        Calls the engine to set a modal text on the screen.

        Returns: None
        """
        self.__engine.set_modal_text(title_modal, msg)

    def set_models_polygon_mode(self, polygon_mode: OGLConstant.IntConstant) -> None:
        """
        Select if the models uses the wireframe mode or not.

        Args:
            polygon_mode: OpenGL polygon mode to draw the model.

        Returns: None
        """
        for model in self.__model_hash.values():
            model.polygon_mode = polygon_mode

    def set_polygon_name(self, polygon_id: str, new_name: str) -> None:
        """
        Change the name of a polygon.

        Args:
            polygon_id: Old polygon id
            new_name: New polygon id

        Returns: None
        """
        if polygon_id in self.__polygon_hash:
            self.__polygon_hash[polygon_id].set_name(new_name)

    def set_polygon_param(self, polygon_id: str, key: str, value: any) -> None:
        """
        Set a new parameter in the polygon.

        Args:
            polygon_id: ID of the polygon.
            key: Key to add to the parameters.
            value: Value of the parameter.

        Returns: None
        """
        try:
            self.__polygon_hash[polygon_id].set_new_parameter(key, value)
            return
        except KeyError:
            # noinspection PyTypeChecker
            raise NonExistentPolygonError(f'Polygon {polygon_id} does not exist in the program')

    def set_thread_task(self, parallel_task, then):
        """
        Set a parallel task in the engine.

        Args:
            parallel_task: Task to execute in parallel
            then: Task to execute after the parallel task

        Returns: None
        """
        self.__engine.set_thread_task(parallel_task, then)

    def transform_points(self, polygon_id: str, model_id: str, min_height: float,
                         max_height: float, transformation_type: str, filters=None) -> None:
        """
        Modify the points inside the polygon from the specified model using a linear transformation.

        Args:
            filters: List with the filters to use in the modification of the points. List must be in the
                format [(filter_id, args),...]
            transformation_type: type of transformation to use.
            polygon_id: ID of the polygon to use.
            model_id: Model to modify.
            min_height: Min target height.
            max_height: Max target height.

        Returns: None
        """
        if filters is None:
            filters = []

        # depending on the type of transformation, calls the respective function to do the transformation.
        if transformation_type == 'linear':
            self.__transform_points_using_linear_transformation(polygon_id,
                                                                model_id,
                                                                min_height,
                                                                max_height,
                                                                filters)

        else:
            raise ModelTransformationError(1)

    def update_3D_model(self, model_id: str) -> None:
        """
        Ask the 3D model to update its values from the 2D model.

        Args:
            model_id: id of the model to update.

        Returns: None
        """
        self.__3d_model_hash[model_id].update_values_from_2D_model()

    def update_models_colors(self) -> None:
        """
        Update the colors of the models reloading the colors from the file used in the program.

        Returns: None
        """
        color_file = self.__engine.get_cpt_file()
        for model in self.__model_hash.values():
            model.set_color_file(color_file)

    def update_models_projection_matrix(self) -> None:
        """
        Update the projection matrix of the models.

        Returns: None
        """
        log.debug("Updating projection matrix of models.")
        scene_data = self.__engine.get_scene_setting_data()

        for model in self.__model_hash.values():
            model.calculate_projection_matrix(scene_data, self.get_zoom_level())

        for model in self.__3d_model_hash.values():
            model.calculate_projection_matrix()

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
