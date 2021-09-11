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
File that contain the Scene class. This class is in charge of the management of the models of the scene.

Class is in charge of the drawing of the models2D, models3D and polygons.
"""
from pathlib import Path
from typing import Dict, List, TYPE_CHECKING, Union

import OpenGL.GL as GL
# noinspection PyPep8Naming
import OpenGL.constant as OGLConstant
import numpy as np

from src.engine.scene.camera import Camera
from src.engine.scene.model.lines import Lines
from src.engine.scene.model.map2dmodel import Map2DModel
from src.engine.scene.model.map3dmodel import Map3DModel
from src.engine.scene.model.model import Model
from src.engine.scene.model.polygon import Polygon
from src.engine.scene.model.tranformations.transformations import ortho, perspective
from src.engine.scene.transformation_helper import TransformationHelper
from src.error.interpolation_error import InterpolationError
from src.error.model_transformation_error import ModelTransformationError
from src.error.scene_error import SceneError
from src.utils import get_logger

if TYPE_CHECKING:
    from engine.engine import Engine

log = get_logger(module="SCENE")

# List with all the filters accepted by the scene to modify the height of the maps
FILTER_LIST = ['is_in', 'is_not_in', 'height_less_than', 'height_greater_than']


class Scene:
    """
    Class in charge of all the elements that are rendered using Opengl.

    This class manage all the configurations needed to show the models in the screen and the different operations
    that the user can do over the models (modify height, interpolate, smoothing).

    In the 2D mode, the class draw the maps in 2D (Map2DModel) and the polygons with or without the interpolation area.
    In the 3D mode, the class only draw the maps in 3D (Map3DModel).
    """

    def __init__(self, engine: 'Engine'):
        """
        Constructor of the class.

        It is necessary to give an engine to the scene so the class can get the settings related to the scene and the
        camera.

        Args:
            engine: Engine of the program.
        """

        # Dictionaries storing the id representing each model and the model itself
        # ------------------------------------------------------------------------
        self.__model_hash: Dict[str, 'Map2DModel'] = {}
        self.__3d_model_hash: Dict[str, 'Map3DModel'] = {}
        self.__polygon_hash: Dict[str, 'Polygon'] = {}
        self.__interpolation_area_hash: Dict[str, List['Model']] = {}

        # Polygons can be draw in different orders, this list store the priority of each polygon so the polygon with
        # high priority can be draw over the polygons with less priority. Polygons that are not in the list will not
        # be draw.
        self.__polygon_draw_priority: List[str] = []

        # Polygons can be draw in different orders, this list store the priority of each model so the models with
        # high priority can be draw over the models with less priority. Models that are not in the list will not
        # be draw.
        self.__model_draw_priority: List[str] = []

        # Variables used by the scene to execute the main logic
        # -----------------------------------------------------
        self.__engine = engine
        self.__camera = Camera()
        self.__width_viewport: int = 0
        self.__height_viewport: int = 0

        # Variables used to calculate the projection matrix used on the scene
        # -------------------------------------------------------------------
        self.__projection_matrix_2D = None
        self.__x = [-180, 180]  # Range of values to show on the scene by default
        self.__y = [-90, 90]  # Range of values to show on the scene by default
        self.__left_coordinate = None  # Left coordinate showed on the scene
        self.__right_coordinate = None  # Right coordinate showed on the scene
        self.__bottom_coordinate = None  # Bottom coordinate showed on the scene
        self.__top_coordinate = None  # Top coordinate showed on the scene
        self.__projection_z_axis_min_value = -99999
        self.__projection_z_axis_max_value = 99999

        self.__projection_matrix_3D = None

        # Auxiliary variables
        # -------------------

        # Variable that indicate which function to use when there is
        # more than one model on the scene.
        self.__should_execute_then_reload: int = 0
        self.__should_execute_then_optimize_gpu_memory: int = 0

        # Variables that count the amount of ID given to the models and polygons
        self.__polygon_id_count: int = 0
        self.__model_id_count: int = 0

    def __process_filters(self, filters=None):
        """
        Given a list with the filters in the format [(id_filter, args),...], format them in a format suitable to
        use in the TransformationHelper class.

        The list of accepted filters and its arguments are as follows:
            height_less_than: int/float
            height_greater_than: int/float
            is_in: str (polygon id)
            is_not_in: str (polygon id)

        Use of filters not listed here or in the FILTER_LIST variable of the module will raise a
        NotImplemented error.

        Args:
            filters: Filters to use in the format [(id_filter, args),...].

        Returns:
            List with the filters and the data necessary to apply them. For example:

            [('height_less_than', 199),
             ('height_greater_than', 400),
             ('is_in', [(0,0), (50,0), ...], # Argument is the list of points of the polygon
             ('is_not_in', [(0,0), (50,0), ...]) # Argument is the list of points of the polygon
        """
        if filters is None:
            filters = []

        filter_data = []
        for filter_obj in filters:
            id_filter = filter_obj[0]

            # check if the filter is accepted by the scene
            if id_filter not in FILTER_LIST:
                raise NotImplementedError(f'Can not process filter with ID {id_filter} since it is not in the list '
                                          f'of accepted filters.')

            # height filters
            if id_filter == 'height_less_than' or id_filter == 'height_greater_than':
                height = float(filter_obj[1])
                filter_data.append((id_filter, height))

            # polygon filters
            elif id_filter == 'is_in' or id_filter == 'is_not_in':
                # get the points of the polygon
                polygon_id = filter_obj[1]

                # Get the data and check it
                # -------------------------
                # Check if the polygon is simple/planar or not. If not, raise exception.
                if not self.is_polygon_planar(polygon_id):
                    raise ModelTransformationError(8)

                # Get vertices of polygon. raise exception if the is problems getting the information.
                try:
                    polygon_points = self.get_polygon_points(polygon_id)

                except SceneError:  # polygon not found
                    raise ModelTransformationError(6)

                # Check that have at least three vertices
                if len(polygon_points) < 9:
                    raise ModelTransformationError(7)

                # Store the data
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

        The process is done in a thread different from the main. While the process is done, a loading frame is rendered
        in the program.

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

        # Ask the model and polygon for the parameters to calculate the new height
        vertices_shape = model.get_vertices_shape()
        vertex_array = model.get_vertices_array().reshape(vertices_shape)
        height_array = model.get_height_array().reshape((vertices_shape[0], vertices_shape[1]))
        polygon_points = polygon.get_point_list()

        if len(polygon_points) < 9:
            raise ModelTransformationError(2)

        if not polygon.is_planar():
            raise ModelTransformationError(3)

        # Process the filters to format them in a format suitable the TransformationHelper class.
        # ---------------------------------------------------------------------------------------
        filter_data = self.__process_filters(filters)

        # CALL THE THREAD TASK
        # --------------------
        # Define mutable object to store results to use from the parallel task to the then task
        new_height = [None]

        # noinspection PyMissingOrEmptyDocstring,PyShadowingNames,PyUnresolvedReferences
        def parallel_task(new_height: list, vertex_array: 'numpy.array', height_array: 'numpy.array',
                          polygon_points: list, max_height: float, min_height: float, filter_data: list):
            # Calculate the new height of the points
            new_height[0] = TransformationHelper().modify_points_inside_polygon_linear(vertex_array,
                                                                                       height_array,
                                                                                       polygon_points,
                                                                                       max_height,
                                                                                       min_height,
                                                                                       filter_data)

        # noinspection PyMissingOrEmptyDocstring,PyShadowingNames,PyUnresolvedReferences
        def then(new_height: list, engine: 'Engine', model: Map2DModel):
            # Tell the polygon the new height of the vertices
            model.update_heights(new_height[0])
            engine.set_program_loading(False)

        # Define the parallel functions to use
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

        This method should be called only when testing or experimenting, to load a new model to the program use the
        method refresh_with_model_2d_async, that method will load the model on the scene and add it to the scene.

        Args:
            model: Model to add to the hashtable.

        Returns: None
        """
        self.__model_hash[model.id] = model

    def add_new_vertex_to_active_polygon_using_map_coords(self, x_coord: float, y_coord: float) -> None:
        """
        Add a new point to the active polygon using the coordinates of the map.

        The coordinates given in the parameters will not be processed, the point added to the polygon will have the
        same coordinates specified on the arguments.

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

        The coordinates expected as arguments are screen coordinates, these coordinates have the
        origin at the top-left of the screen with the x-axis positive to the right and the y-axis positive to the
        bottom. The coordinates given as parameters will be processed and transformed to the coordinates used in the
        map being showed on the scene.

        The new vertex will not be added if it falls outside of the space considered for the scene on the program, but
        will be added if it falls outside of the map (but still inside of the scene).

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
            new_x, new_y = self.calculate_map_position_from_window(position_x,
                                                                   position_y,
                                                                   allow_outside_map=True,
                                                                   allow_outside_scene=False)
            self.__polygon_hash[active_polygon].add_point(new_x, new_y)

    def add_polygon(self, polygon: 'Polygon') -> None:
        """
        Add a new polygon to render on the scene.

        This method should only be called on testing on experimenting. To add a new polygon to the scene call the
        method create_new_polygon, this method will create a polygon and add it to the scene to be rendered.

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

        model.update_heights(new_heights)

    def calculate_map_position_from_window(self, position_x: int, position_y: int, allow_outside_map=False,
                                           allow_outside_scene=False) -> (float, float):
        """
        Calculate the position of a point on the map currently being showed on the screen.

        Returns (None, None) if there is no active model on the program or if the position of the mouse is outside of
        the map.

        Args:
            allow_outside_map: If to enable to calculate the map position even when the positions given fall outside of
                               the rendered map. When disabled, (None, None) is returned if points are outside of map.
            allow_outside_scene: If to enable to calculate the map position when the position given fall outside of
                                 the scene. When disabled, (None, None) is returned if points are outside of map.
            position_x: Window position x of the point. (pixels to the right on the window)
            position_y: Window position y (from top to bottom) of the point. (pixels down on the window)

        Returns: position_x, position_y of the new point in the map coordinates.
        """
        # Security verifications
        # ----------------------

        # Model has to exist on the program
        if self.__engine.get_active_model_id() is None:
            return None, None

        # Model must be initialized to obtain the data
        x_array, y_array = self.get_active_model_coordinates_arrays()
        if x_array is None and y_array is None:
            return None, None

        # Calculate the position of the mouse on the map
        # ----------------------------------------------
        scene_settings = self.__engine.get_scene_setting_data()
        map_positions = self.get_2D_showed_limits()
        window_settings = self.__engine.get_window_setting_data()

        x_dist_pixel = position_x - scene_settings['SCENE_BEGIN_X']
        y_dist_pixel = (window_settings['HEIGHT'] - position_y) - scene_settings['SCENE_BEGIN_Y']

        scene_x = scene_settings['SCENE_WIDTH_X']
        scene_y = scene_settings['SCENE_HEIGHT_Y']

        x_pos = map_positions['left'] + (map_positions['right'] - map_positions['left']) * x_dist_pixel / scene_x
        y_pos = map_positions['bottom'] + (map_positions['top'] - map_positions['bottom']) * y_dist_pixel / scene_y

        # Return None, None if mouse is outside the map.
        # ----------------------------------------------
        outside_map = x_pos < np.min(x_array) or \
                      x_pos > np.max(x_array) or \
                      y_pos < np.min(y_array) or \
                      y_pos > np.max(y_array)
        if (not allow_outside_map) and outside_map:
            return None, None

        # Return None, None if the mouse is outside of the scene.
        # -------------------------------------------------------
        outside_scene = position_x < scene_settings['SCENE_BEGIN_X'] or \
                        position_x > scene_settings['SCENE_BEGIN_X'] + scene_settings['SCENE_WIDTH_X'] or \
                        position_y > window_settings['HEIGHT'] - scene_settings['SCENE_BEGIN_Y'] or \
                        position_y < window_settings['HEIGHT'] - (scene_settings['SCENE_BEGIN_Y'] +
                                                                  scene_settings['SCENE_HEIGHT_Y'])
        if (not allow_outside_scene) and outside_scene:
            return None, None

        # Return the calculated value on the map.
        # ---------------------------------------
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

    def change_polygon_draw_priority(self, polygon_id: str, new_priority: int) -> None:
        """
        Change the order on which the polygons are draw on the scene.

        The closer the priority is to 0, the higher the priority. Polygons with high priority will be draw over 
        polygons with less priority.

        Args:
            polygon_id: ID of the polygon to modify the draw order.
            new_priority: New priority to be assigned to the polygon.

        Returns: None
        """
        # Check that polygon exists in the scene
        if polygon_id not in self.__polygon_hash.keys():
            raise SceneError(5)

        # Remove the polygon from the drawing list, raise exception if it is not in the list
        try:
            self.__polygon_draw_priority.remove(polygon_id)
        except ValueError:
            raise SceneError(6)

        # Insert element in the new position
        self.__polygon_draw_priority.insert(new_priority, polygon_id)

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
    def create_3D_model_if_not_exists(self) -> None:
        """
        Create a new map3Dmodel object and add it to the scene.

        By default, the data used to generate the model is the one of the active model on the scene.

        Returns: Id of the new map3Dmodel
        """
        self.reset_camera_values()
        new_model = Map3DModel(self, self.__model_hash[self.__engine.get_active_model_id()])
        new_model.id = self.__engine.get_active_model_id()

        # add the model to the hash
        self.__3d_model_hash[self.__engine.get_active_model_id()] = new_model

    def create_new_polygon(self, point_list: list = None, parameters: dict = None,
                           priority_position: int = None) -> str:
        """
        Create a new polygon and adds it to the list of polygons of the scene.

        Optionally, a list of points and a dictionary of parameters can be specified to set as initial values on the
        polygon. The list of points must define a simple/planar polygon, otherwise, an LineIntersectionError or
        RepeatedPointError will be raised.

        Args:
            priority_position: Where, in the draw order, set the polygon. Negative values will place the polygon at the end
                               of the list (will be draw the last).
            point_list: List with the points to add to the polygon. [[x,y],[x,y],...]
            parameters: Parameters to set in the polygon. {parameter_name:value,...}

        Returns: id of the created polygon
        """

        # Generate a new id for the polygon
        # ---------------------------------
        new_polygon_id = f"Polygon {self.__polygon_id_count}"

        # Add the id to the list of drawing polygons
        # ------------------------------------------
        if priority_position is None:
            self.__polygon_draw_priority.append(new_polygon_id)
        else:
            self.__polygon_draw_priority.insert(priority_position, new_polygon_id)

        # Create the polygon and return its id
        # ------------------------------------
        polygon = Polygon(self, new_polygon_id, point_list, parameters)
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

            # remove it from the draw list
            if polygon_id in self.__polygon_draw_priority:
                self.__polygon_draw_priority.remove(polygon_id)

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
            raise SceneError(5)

    def draw(self) -> None:
        """
        Draw the models in the hash of models.

        Depending on the mode of the program (2D or 3D), the models draw on the scene will be different. In the 2D
        mode, the polygons and the 2D map will be draw, while in the 3D mode only the 3D maps will be rendered.

        If the mode selected is 3D and there is no 3D model for the current loaded map, the the model will be generated
        in place.

        Returns: None
        """

        # get the active model
        active_model = self.__engine.get_active_model_id()

        # check if draw the 2D or the 3D of the models.
        if self.__engine.get_program_view_mode() == '2D':

            # Draw all the Map2DModels
            for model_2d in reversed(self.__model_draw_priority):
                # Change the height of the maps and draw them
                self.__model_hash[model_2d].draw()

            # Draw all the interpolation areas
            for area_models in self.__interpolation_area_hash.values():
                for model in area_models:
                    model.draw()

            # Draw all the polygons
            for polygon in reversed(self.__polygon_draw_priority):
                # Change the height of the polygon depending on the draw order and draw them
                self.__polygon_hash[polygon].draw()

        elif self.__engine.get_program_view_mode() == '3D':

            # Draw model if it exists
            if active_model in self.__3d_model_hash:
                self.__3d_model_hash[active_model].draw()

    # noinspection PyUnresolvedReferences
    def get_projection_matrix_2D(self) -> np.array:
        """
        Get the projection matrix from the active 2D model being showed on the screen.

        The projection matrix of the 2D models limit the coordinates showed on the screen depending on the position
        of the map and the level of zoom. This method is useful when rendering objects that need to be over the 2D
        map.

        The projection matrix used in 2D mode are orthogonal, and the camera is always on the z-axis coordinate, so the
        value for near/far in the matrix does not affect the way that the models are viewed on the scene. Even with
        this, models draw in the 2D mode that have a z-coordinate value that is outside the near/far range will not be
        rendered (since they are out of the projection matrix).

        The near/far range is the one used by the Map2DModel class for their projection matrix. That should
        be [-99999, 99999]. Points that use this matrix and have points with z-axis coordinate outside this range
        will not be rendered.

        Returns: array with the projection matrix of the active model.
        """
        if self.__projection_matrix_2D is None:
            self.update_projection_matrix_2D()

        return self.__projection_matrix_2D

    def get_projection_matrix_3D(self) -> np.array:
        """
        Return the projection matrix to use when rendering 3D models.

        Returns: Projection matrix to use when rendering 3D models.
        """
        if self.__projection_matrix_3D is None:
            self.update_projection_matrix_3D()

        return self.__projection_matrix_3D

    def get_active_model_coordinates_arrays(self) -> (Union[np.ndarray, None], Union[np.ndarray, None]):
        """
        Get two arrays, the first containing the coordinates used in the active model for the x-axis and the second
        containing the coordinates used in the active model for the y-axis.

        The lists can be sorted ascended or descended. (must be verified, can vary)

        If there is no active model or if there is a problem retrieving the model, then (None, None) is returned.

        Returns: (x-axis array, y-axis array) coordinates used in the active model.
        """
        active_model_id = self.__engine.get_active_model_id()
        if active_model_id in self.__model_hash:
            model = self.__model_hash[active_model_id]
            return model.get_model_coordinate_array()
        else:
            return None, None

    def get_active_model_height_on_coordinates(self, x_coordinate: float, y_coordinate: float) -> Union[float, None]:
        """
        Get the height of the active model in the specified coordinates.

        If coordinates are outside the model or there is no active model, then None is returned.

        Args:
            x_coordinate: x-axis coordinate.
            y_coordinate: y-axis coordinate.

        Returns: Height of the model in the coordinates.
        """
        active_model_id = self.__engine.get_active_model_id()
        if active_model_id in self.__model_hash:
            return self.__model_hash[active_model_id].get_height_on_coordinates(x_coordinate, y_coordinate)
        else:
            return None

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

    def get_2D_showed_limits(self) -> dict:
        """
        Get a dictionary with the limits of the model being showed on the screen.

        Returns: Dictionary with the limits showing on the scene
        """
        if self.__left_coordinate is None or \
                self.__right_coordinate is None or \
                self.__top_coordinate is None or \
                self.__bottom_coordinate is None:
            self.update_projection_matrix_2D()

        return {
            'left': self.__left_coordinate,
            'right': self.__right_coordinate,
            'top': self.__top_coordinate,
            'bottom': self.__bottom_coordinate
        }

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

    def get_model_list(self) -> List[str]:
        """
        Get a list with the ID of all the 2D models loaded into the program.

        Returns: List with the ID of the models.
        """
        return list(self.__model_hash.keys())

    def get_model_information(self, model_id: str) -> dict:
        """
        Get the information related to a model on the program.

        The dictionary generated has the following shape:
        {
            'height_array': Numpy array
            'coordinates_array': (Numpy array, Numpy array),
            'projection_matrix': Numpy array,
            'showed_limits': {
                'left': Number,
                'right': Number,
                'top': Number,
                'bottom': Number
            },
            'shape': (Int, Int, Int),
            'name': string
        }

        Any parameter can be None if the model has not been initialized yet.

        Returns: Dictionary with the information of the model.
        """
        model = self.__model_hash[model_id]
        return {
            'height_array': model.get_height_array(),
            'coordinates_array': model.get_model_coordinate_array(),
            'projection_matrix': self.get_projection_matrix_2D(),
            'showed_limits': self.get_2D_showed_limits(),
            'shape': model.get_vertices_shape(),
            'name': model.get_name()
        }

    def get_3d_model_list(self) -> List[str]:
        """
        Get a list with the ID of the 3D models generated on the program.

        The ID used by the 3D models is the same as the ID used by the 2D model from which they were generated. All 3D
        models have a 2D model associated, but not all 2D models have a 3D model.

        Returns: List with the ID of the 3D models generated on the program.
        """
        return list(self.__3d_model_hash.keys())

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
            raise SceneError(5)

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
            raise SceneError(5)

    def get_polygon_points(self, polygon_id: str) -> list:
        """
        Return the list of points of a polygon.
        The points are formatted as follows: [x1, y1, z1, x2, y2, z2, ...]

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
        Interpolate the points at the exterior of the polygon using the given interpolation type.

        Possible interpolation types:
            - linear
            - nearest
            - cubic

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
            map2d_model.update_heights(new_height)
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

    def load_preview_interpolation_area(self, distance: float, polygon_id: str) -> None:
        """
        Calculate the interpolation area for the active polygon and draw it on the scene.

        WARNING: in case of generating the area, it can be time expensive and in some cases, inaccurate.

        Args:
            polygon_id: id of the polygon to load the interpolation area.
            distance: Distance to use to calculate the external area.

        Returns: None
        """
        # generating polygon
        polygon = self.__polygon_hash[polygon_id]
        polygon_points = polygon.get_point_list()

        # raise error in case polygon does not have enough points
        if len(polygon_points) < 9:
            raise SceneError(2)

        polygon_external_points = polygon.get_exterior_polygon_points(distance)

        # generating lines model
        lines_external = Lines(self, point_list=np.array(polygon_external_points).reshape((-1, 3)))
        lines_external.set_line_color([1, 0, 0, 0.5])

        # Deprecated Code
        # ---------------
        # # Add the lines of the external polygon to the lines model
        # for ind in range(int(len(polygon_external_points) / 3)):
        #
        #     point_1 = (polygon_external_points[ind * 3],
        #                polygon_external_points[ind * 3 + 1],
        #                polygon_external_points[ind * 3 + 2])
        #
        #     if ind == len(polygon_external_points) / 3 - 1:
        #         point_2 = (polygon_external_points[0],
        #                    polygon_external_points[1],
        #                    polygon_external_points[2])
        #     else:
        #         point_2 = (polygon_external_points[ind * 3 + 3],
        #                    polygon_external_points[ind * 3 + 4],
        #                    polygon_external_points[ind * 3 + 5])
        #   lines_external.add_line(point_1, point_2)

        # Add the model to the hash of interpolation areas
        self.__interpolation_area_hash[self.__engine.get_active_polygon_id()] = [lines_external]

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

    def load_model_from_file_async(self, path_color_file: str, path_model: str, then=lambda x: None) -> None:
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
        model = Map2DModel(self, name=Path(path_model).name)

        # noinspection PyMissingOrEmptyDocstring
        def then_routine():
            log.debug("Settings colors from file.")
            model.set_color_file(path_color_file)
            self.update_projection_matrix_2D()
            model.wireframes = False

            model.id = str(self.__model_id_count)
            self.__model_draw_priority.append(model.id)
            self.add_model(model)

            self.__model_id_count += 1

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

    def remove_all_3d_models(self) -> None:
        """
        Remove all the 3D models from the hash of 3D models.

        Returns: None
        """
        self.__3d_model_hash = {}

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
        Change the polygon mode used by the models.

        The polygon mode must be one of the following constants defined in the opengl library:
            - GL_POINT
            - GL_LINE
            - GL_FILL

        Args:
            polygon_mode: OpenGL polygon mode to draw the model.

        Returns: None
        """
        for model in self.__model_hash.values():
            model.polygon_mode = polygon_mode

        for model in self.__3d_model_hash.values():
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
            raise SceneError(5)

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

        Transformation types available:
            - linear

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

    def update_projection_matrix_3D(self) -> None:
        """
        Recalculate the projection matrix to use when rendering 3D models.

        Returns: None
        """
        log.debug('Recalculated projection.')
        scene_settings_data = self.__engine.get_scene_setting_data()
        camera_settings_data = self.__engine.get_camera_settings()
        self.__projection_matrix_3D = perspective(camera_settings_data['FIELD_OF_VIEW'],
                                                  scene_settings_data['SCENE_WIDTH_X'] / scene_settings_data[
                                                      'SCENE_HEIGHT_Y'],
                                                  camera_settings_data['PROJECTION_NEAR'],
                                                  camera_settings_data['PROJECTION_FAR'])

    def update_projection_matrix_2D(self) -> None:
        """
        Generate the projection matrix on the model. Method must be called before drawing.

        The projection matrix is the one in charge of converting the coordinates from the view space (camera point of
        view) into the range (-1, 1), when the points are converted to this range of coordinates it is
        called that they are in the clip space.

        OpenGL is the one in charge of converting the coordinates from the clipping space into the screen space. showing
        the points on the screen.

        Since the projection matrix is the one who converts the coordinates of the model into the space accepted by
        OpenGL (-1, 1), the matrix is also the one in charge of keeping the aspect ratio of the models
        showed on the screen.

        More information in: https://learnopengl.com/Getting-started/Coordinate-Systems

        Returns: None
        """

        # Get the data and the proportions to generate the projection matrix
        # ------------------------------------------------------------------
        map_position = self.__engine.get_map_position()
        scene_data = self.__engine.get_scene_setting_data()
        zoom_level = self.__engine.get_zoom_level()

        width_scene = scene_data['SCENE_WIDTH_X']
        height_scene = scene_data['SCENE_HEIGHT_Y']
        proportion_panoramic = width_scene / float(height_scene)
        proportion_portrait = height_scene / float(width_scene)

        # maximum and minimum values of the map coordinates.
        min_x = min(self.__x)
        max_x = max(self.__x)
        min_y = min(self.__y)
        max_y = max(self.__y)

        # width and height of the loaded maps.
        width_map = max_x - min_x
        height_map = max_y - min_y

        # CASE PANORAMIC DATA
        # -------------------
        if width_map > height_map:
            # calculate the height of the viewport on map coordinates
            # the width of the viewport in map coordinates is the same as x_width
            calculated_height_viewport = width_map / proportion_panoramic

            # calculates the coordinates to use to clip the map on the scene to keep the aspect ratio.
            projection_min_y = (max_y + min_y) / 2 - calculated_height_viewport / 2
            projection_max_y = (max_y + min_y) / 2 + calculated_height_viewport / 2

            # Calculate the distance to use as offset when applying zoom on the maps.
            zoom_difference_x = (width_map - (width_map / zoom_level)) / 2
            zoom_difference_y = (calculated_height_viewport - (calculated_height_viewport / zoom_level)) / 2

            # calculate the coordinates to show on the viewport.
            # NOTE: The coordinates can be values outside of the map.
            self.__left_coordinate = min_x + zoom_difference_x
            self.__right_coordinate = max_x - zoom_difference_x
            self.__bottom_coordinate = projection_min_y + zoom_difference_y
            self.__top_coordinate = projection_max_y - zoom_difference_y

        # CASE PORTRAIT DATA
        # -------------------
        else:
            # calculate the width of the viewport on map coordinates
            # the width of the viewport in map coordinates is the same as x_width
            calculated_width_viewport = height_map / proportion_portrait

            # calculates the coordinates to use to clip the map on the scene to keep the aspect ratio.
            projection_min_x = (max_x + min_x) / 2 - calculated_width_viewport / 2
            projection_max_x = (max_x + min_x) / 2 + calculated_width_viewport / 2

            # Calculate the distance to use as offset when applying zoom on the maps.
            zoom_difference_y = (height_map - (height_map / zoom_level)) / 2
            zoom_difference_x = (calculated_width_viewport - (calculated_width_viewport / zoom_level)) / 2

            # calculate the coordinates to show on the viewport.
            # NOTE: The coordinates can be values outside of the map.
            self.__left_coordinate = projection_min_x + zoom_difference_x
            self.__right_coordinate = projection_max_x - zoom_difference_x
            self.__bottom_coordinate = min_y + zoom_difference_y
            self.__top_coordinate = max_y - zoom_difference_y

        # Move the coordinates to show on the model depending on the position that the model is located.
        self.__left_coordinate -= map_position[0]
        self.__right_coordinate -= map_position[0]
        self.__top_coordinate -= map_position[1]
        self.__bottom_coordinate -= map_position[1]

        # Calculate the projection matrix given the calculated coordinates to show on the model.
        self.__projection_matrix_2D = ortho(self.__left_coordinate,
                                            self.__right_coordinate,
                                            self.__bottom_coordinate,
                                            self.__top_coordinate,
                                            self.__projection_z_axis_min_value,
                                            self.__projection_z_axis_max_value)

    def update_viewport(self) -> None:
        """
        Update the viewport with the new values that exist in the Settings.
        """
        log.debug("Updating viewport")
        self.update_viewport_variables()

        scene_data = self.__engine.get_scene_setting_data()
        GL.glViewport(scene_data['SCENE_BEGIN_X'], scene_data['SCENE_BEGIN_Y'], scene_data['SCENE_WIDTH_X'],
                      scene_data['SCENE_HEIGHT_Y'])

        self.update_projection_matrix_2D()
        self.update_projection_matrix_3D()

    def update_viewport_variables(self):
        """
        Update the viewport variables.

        Returns: None
        """
        viewport_data = self.__engine.get_scene_setting_data()
        self.__width_viewport = viewport_data['SCENE_WIDTH_X']
        self.__height_viewport = viewport_data['SCENE_HEIGHT_Y']
