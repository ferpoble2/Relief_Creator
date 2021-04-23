"""
File with the definition of the class Map3DModel, class in charge of the 3D representation of the maps.
"""
import ctypes as ctypes

import numpy as np
import OpenGL.GL as GL

from src.input.CTP import read_file
from src.engine.scene.model.mapmodel import MapModel
from src.engine.scene.model.tranformations.transformations import perspective, identity
from src.engine.scene.unit_converter import UnitConverter

from src.utils import get_logger

from src.type_hinting import *

log = get_logger(module='MAP3DMODEL')


class Map3DModel(MapModel):
    """
    Class that manage all things related to the representation in 3D of the maps.
    """

    def __init__(self, scene: 'Scene', model_2d: 'Map2DModel', height_measure_unit: str = 'meters',
                 vertices_measure_unit: str = 'degrees'):
        """
        Constructor of the class.
        """
        super().__init__(scene)

        self.set_shaders("./engine/shaders/model_3d_vertex.glsl",
                         "./engine/shaders/model_3d_fragment.glsl")

        # variables used for the coloration of the model
        self.__color_file = ''
        self.__colors = []
        self.__height_limit = []

        # measure unit used in the model.
        self.__height_measure_unit = height_measure_unit
        self.__vertices_measure_unit = vertices_measure_unit

        # 2D model to use for the reload process
        self.__model_2D_used = model_2d

        # factor for the user to view
        self.__height_exaggeration_factor = 1

        # internal factor to convert different measure units
        self.__height_conversion_factor = self.__get_conversion_factor()

        # quality of the 3D model (0 is maximum)
        self.__quality = 0

        # matrices used for the rendering
        self.__model = identity()
        self.__view = self.scene.get_camera_view_matrix()

        # arrays to use to store the heights of the model on gpu
        self.hbo = GL.glGenBuffers(1)
        self.__height_array = model_2d.get_height_array().copy()
        self.__max_height = 0
        self.__min_height = 0

        # shape of the map
        self.__vertices_shape = model_2d.get_vertices_shape()

        # projection matrix to use for the rendering
        scene_settings_data = self.scene.get_scene_setting_data()
        camera_settings_data = self.scene.get_camera_settings()
        self.__projection = perspective(camera_settings_data['FIELD_OF_VIEW'],
                                        scene_settings_data['SCENE_WIDTH_X'] / scene_settings_data['SCENE_HEIGHT_Y'],
                                        camera_settings_data['PROJECTION_NEAR'],
                                        camera_settings_data['PROJECTION_FAR'])

        # set the data for the model
        # --------------------------
        self.update_values_from_2D_model()

    def __set_height_buffer(self) -> None:
        """
        Set the buffer object for the heights to be used in the shaders.

        IMPORTANT:
            Uses the index 1 of the attributes pointers.

        Returns: None

        """
        height = np.array(self.__height_array, dtype=np.float32)

        # Set the buffer data in the buffer
        GL.glBindVertexArray(self.vao)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.hbo)
        GL.glBufferData(GL.GL_ARRAY_BUFFER,
                        len(height) * self.scene.get_float_bytes(),
                        height,
                        GL.GL_STATIC_DRAW)

        # Enable the data to the shaders
        GL.glVertexAttribPointer(1, 1, GL.GL_FLOAT, GL.GL_FALSE, 0, ctypes.c_void_p(0))
        GL.glEnableVertexAttribArray(1)

        return

    def __get_conversion_factor(self) -> float:
        """
        Get the conversion factor to use to change the height of the model to match the measure units used
        on the map.

        Returns: float
        """
        factor_generator = UnitConverter()
        if self.__vertices_measure_unit == 'degrees':
            if self.__height_measure_unit == 'meters':
                return factor_generator.meter_to_degrees()

            elif self.__height_measure_unit == 'kilometers':
                return factor_generator.kilometer_to_meter() * factor_generator.meter_to_degrees()

            else:
                raise NotImplementedError(f'Conversion of unit {self.__height_measure_unit} not implemented '
                                          f'in the model 3D')
        else:
            raise NotImplementedError(f'Conversion of unit {self.__vertices_measure_unit} not implemented '
                                      f'in the model 3D')

    def _update_uniforms(self) -> None:
        """
        Method to update the uniforms used in the shader programs.

        Returns: None
        """
        model_location = GL.glGetUniformLocation(self.shader_program, "model")
        view_location = GL.glGetUniformLocation(self.shader_program, "view")
        projection_location = GL.glGetUniformLocation(self.shader_program, "projection")
        max_height_location = GL.glGetUniformLocation(self.shader_program, "max_height")
        min_height_location = GL.glGetUniformLocation(self.shader_program, "min_height")

        # set the value
        GL.glUniformMatrix4fv(model_location, 1, GL.GL_TRUE, self.__model)
        GL.glUniformMatrix4fv(view_location, 1, GL.GL_TRUE, self.__view)
        GL.glUniformMatrix4fv(projection_location, 1, GL.GL_TRUE, self.__projection)
        GL.glUniform1f(max_height_location, float(self.__max_height))
        GL.glUniform1f(min_height_location, float(self.__min_height))

        # set colors if using
        if self.__color_file is not None:
            colors_location = GL.glGetUniformLocation(self.shader_program, "colors")
            height_color_location = GL.glGetUniformLocation(self.shader_program, "height_color")
            length_location = GL.glGetUniformLocation(self.shader_program, "length")

            GL.glUniform3fv(colors_location, len(self.__colors), self.__colors)
            GL.glUniform1fv(height_color_location, len(self.__height_limit), self.__height_limit)
            GL.glUniform1i(length_location, len(self.__colors))

    def calculate_projection_matrix(self) -> None:
        """
        Recalculate the projection matrix to use to draw the model.

        Returns: None
        """
        log.debug('Recalculated projection.')
        scene_settings_data = self.scene.get_scene_setting_data()
        camera_settings_data = self.scene.get_camera_settings()
        self.__projection = perspective(camera_settings_data['FIELD_OF_VIEW'],
                                        scene_settings_data['SCENE_WIDTH_X'] / scene_settings_data['SCENE_HEIGHT_Y'],
                                        camera_settings_data['PROJECTION_NEAR'],
                                        camera_settings_data['PROJECTION_FAR'])

    def change_height_measure_unit(self, new_measure_unit: str) -> None:
        """
        Change the measure unit used in the model.

        Args:
            new_measure_unit: New measure unit to use in the model.

        Returns: None
        """
        self.__height_measure_unit = new_measure_unit

    def change_height_normalization_factor(self, new_value) -> None:
        """
        Change the normalization factor used to modify the heights of the model.

        Do nothing if the new factor is the same than the previous one.

        Args:
            new_value: New interpolation factor.

        Returns: None
        """

        # do nothing if the value is the same than the before.
        if self.__height_exaggeration_factor == new_value:
            return

        # change the value
        self.__height_exaggeration_factor = new_value

        # modify the vertices array to fit the new heights
        height_array = self.__height_array * self.__height_exaggeration_factor * self.__height_conversion_factor
        height_array = height_array.reshape(self.__vertices_shape[:2])

        vertices_array = self.get_vertices_array().reshape(self.__vertices_shape)
        vertices_array[:, :, 2] = height_array
        self.set_vertices(vertices_array.reshape(-1))

    def change_vertices_measure_unit(self, new_measure_unit: str) -> None:
        """
        Change the measure unit used in the model for the points.

        Args:
            new_measure_unit: New measure unit to use in the model.

        Returns: None
        """
        self.__vertices_measure_unit = new_measure_unit

    def draw(self) -> None:
        """
        Draw the model on the screen.

        Returns: None
        """

        # update the variables
        self.__view = self.scene.get_camera_view_matrix()

        # draw
        super().draw()

    def get_normalization_height_factor(self) -> float:
        """
        Get the normalization height factor being used by the model.

        Returns: factor being used
        """
        return self.__height_exaggeration_factor

    def set_color_file(self, filename: str) -> None:
        """

        Args:
            filename: File to use for the colors.

        Returns: None

        """
        if len(self.get_vertices_array()) == 0:
            raise AssertionError('Did you forget to set the vertices? (set_vertices_from_grid)')

        # set variables
        self.__color_file = filename

        file_data = read_file(filename)
        colors = []
        height_limit = []

        for element in file_data:
            colors.append(element['color'])
            height_limit.append(element['height'])

        # send error in case too many colors are passed
        if len(colors) > 500:
            raise BufferError('Shader used does not support more than 500 colors in the file.')

        self.__colors = np.array(colors, dtype=np.float32)
        self.__height_limit = np.array(height_limit, dtype=np.float32)

    def update_values_from_2D_model(self) -> None:
        """
        Update the vertices and height arrays from the 2D model.

        Returns: None
        """
        log.debug('Updating GPU arrays...')

        # get the shape of the model
        self.__vertices_shape = self.__model_2D_used.get_vertices_shape()

        # get a copy of the arrays to not modify the originals
        vertices_array = self.__model_2D_used.get_vertices_array().copy()

        # get the information about the height
        self.__height_array = self.__model_2D_used.get_height_array().copy()
        self.__max_height = max(self.__height_array)
        self.__min_height = min(self.__height_array)
        self.__set_height_buffer()

        # Convert the height of the points to the corresponding unit and assign it to the vertices.
        # note: self.__height_array must not change since the coloration used depends on the real height assigned to
        #       the points on the netcdf file. only the vertices array must be modified.
        self.__height_conversion_factor = self.__get_conversion_factor()
        height_array_converted = self.__height_array * self.__height_exaggeration_factor * self.__height_conversion_factor
        height_array_converted_squared = height_array_converted.reshape(self.__vertices_shape[:2])

        vertices_array_reshaped = vertices_array.reshape(self.__vertices_shape)
        vertices_array_reshaped[:, :, 2] = height_array_converted_squared
        self.set_vertices(vertices_array_reshaped.reshape(-1))

        # Update the array of indices used in the model
        x_values = vertices_array_reshaped[0, :, 0].reshape(-1)
        y_values = vertices_array_reshaped[:, 0, 1].reshape(-1)
        index_array = self._generate_index_list(self.__quality,
                                                self.__quality,
                                                x_values,
                                                y_values)
        self.set_indices(index_array)

        # set the color file
        self.set_color_file(self.__model_2D_used.get_color_file())
