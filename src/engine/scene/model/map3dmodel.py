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
File with the definition of the class Map3DModel, class in charge of the 3D representation of the maps.
"""
import ctypes as ctypes
from typing import TYPE_CHECKING

import OpenGL.GL as GL
import numpy as np

from src.engine.scene.model.mapmodel import MapModel
from src.engine.scene.model.tranformations.transformations import identity
from src.engine.scene.unit_converter import UnitConverter
from src.input.CTP import read_file
from src.utils import get_logger

if TYPE_CHECKING:
    from src.engine.scene.scene import Scene
    from src.engine.scene.model.map2dmodel import Map2DModel

log = get_logger(module='MAP3D_MODEL')


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

        # Utilities variables
        self.set_shaders("./src/engine/shaders/model_3d_vertex.glsl",
                         "./src/engine/shaders/model_3d_fragment.glsl")
        self.__model_2D_used = model_2d

        # Coloration variables
        # --------------------
        self.__color_file = ''
        self.__colors = []
        self.__height_color_limits = []

        # Vertices variables
        # ------------------
        self.__vertices_measure_unit = vertices_measure_unit
        self.__vertices_shape = model_2d.get_vertices_shape()

        # Height variables
        # ----------------
        self.hbo = GL.glGenBuffers(1)
        self.__height_array = np.array([])  # Unidimensional array

        self.__height_exaggeration_factor = 1
        self.__height_measure_unit = height_measure_unit

        # Rendering variables
        # -------------------
        self.__model = identity()  # Model matrix to use in the rendering
        self.__quality = 0  # Quality of the 3D model (0 is maximum)

        # Set the data for the model
        # --------------------------
        self.update_values_from_2D_model()

    def __set_height_buffer(self, new_height: np.ndarray) -> None:
        """
        Set the buffer object for the heights to be used in the shaders.

        IMPORTANT:
            Uses the index 1 of the attributes pointers.

        Returns: None

        """
        self.__height_array = np.array(new_height, dtype=np.float32).reshape(-1)

        # Set the buffer data in the buffer
        GL.glBindVertexArray(self.vao)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.hbo)
        GL.glBufferData(GL.GL_ARRAY_BUFFER,
                        len(self.__height_array) * self.scene.get_float_bytes(),
                        self.__height_array,
                        GL.GL_STATIC_DRAW)

        # Enable the data to the shaders
        GL.glVertexAttribPointer(1, 1, GL.GL_FLOAT, GL.GL_FALSE, 0, ctypes.c_void_p(0))
        GL.glEnableVertexAttribArray(1)

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

        # set the value
        GL.glUniformMatrix4fv(model_location, 1, GL.GL_TRUE, self.__model)
        GL.glUniformMatrix4fv(view_location, 1, GL.GL_TRUE, self.scene.get_camera_view_matrix())
        GL.glUniformMatrix4fv(projection_location, 1, GL.GL_TRUE, self.scene.get_projection_matrix_3D())

        # set colors if using
        if self.__color_file is not None:
            colors_location = GL.glGetUniformLocation(self.shader_program, "colors")
            height_color_location = GL.glGetUniformLocation(self.shader_program, "height_color")
            length_location = GL.glGetUniformLocation(self.shader_program, "length")

            GL.glUniform3fv(colors_location, len(self.__colors), self.__colors)
            GL.glUniform1fv(height_color_location, len(self.__height_color_limits), self.__height_color_limits)
            GL.glUniform1i(length_location, len(self.__colors))

    def change_height_measure_unit(self, new_measure_unit: str) -> None:
        """
        Change the measure unit used in the model.

        Args:
            new_measure_unit: New measure unit to use in the model.

        Returns: None
        """
        self.__height_measure_unit = new_measure_unit

    def change_height_normalization_factor(self, new_value: float) -> None:
        """
        Change the normalization factor used to modify the heights of the model.

        Do nothing if the new factor is the same than the previous one.

        Args:
            new_value: New interpolation factor.

        Returns: None
        """

        # Do nothing if the value is the same than the before.
        if self.__height_exaggeration_factor == new_value:
            return

        # Update the value
        self.__height_exaggeration_factor = new_value

        # Modify the vertices array to fit the new heights
        height_array = self.__height_array * self.__height_exaggeration_factor * self.__get_conversion_factor()
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
        super().draw()

    def get_normalization_height_factor(self) -> float:
        """
        Get the normalization height factor being used by the model.

        Returns: factor being used
        """
        return self.__height_exaggeration_factor

    def set_color_file(self, filename: str) -> None:
        """
        Set the color file to use for the model.

        Args:
            filename: File to use for the colors.

        Returns: None
        """
        if len(self.get_vertices_array()) == 0:
            raise AssertionError('Did you forget to set the vertices? (set_vertices_from_grid)')

        # Extract the data for the coloration from the file
        # -------------------------------------------------
        self.__color_file = filename

        file_data = read_file(filename)
        colors = []
        height_limit = []

        for element in file_data:
            colors.append(element['color'])
            height_limit.append(element['height'])

        # Store the data of the coloration to be passed to the shader
        # -----------------------------------------------------------
        if len(colors) > 500:
            raise BufferError('Shader used does not support more than 500 colors in the file.')

        self.__colors = np.array(colors, dtype=np.float32)
        self.__height_color_limits = np.array(height_limit, dtype=np.float32)

    def update_values_from_2D_model(self) -> None:
        """
        Update the vertices and height arrays from the 2D model.

        Returns: None
        """
        log.debug('Updating GPU arrays...')

        # Get and set the vertices on the model
        # -------------------------------------
        self.__vertices_shape = self.__model_2D_used.get_vertices_shape()

        # Get a copy of the arrays and transform the height of the points to the same unit as the other coordinates
        # ---------------------------------------------------------------------------------------------------------
        self.__vertices_array = self.__model_2D_used.get_vertices_array().copy()
        self.__vertices_array = self.__vertices_array.reshape(self.__model_2D_used.get_vertices_shape())
        self.__vertices_array[:, :, 2] = self.__vertices_array[:, :, 2] * self.__height_exaggeration_factor * \
                                         self.__get_conversion_factor()
        self.set_vertices(self.__vertices_array.reshape(-1))

        # Get the information about the height
        # ------------------------------------
        self.__set_height_buffer(self.__model_2D_used.get_height_array())

        # Update the array of indices used in the model
        # ---------------------------------------------
        x_values = self.__vertices_array[0, :, 0].reshape(-1)
        y_values = self.__vertices_array[:, 0, 1].reshape(-1)
        index_array = self._generate_index_list(self.__quality,
                                                self.__quality,
                                                x_values,
                                                y_values)
        self.set_indices(index_array)

        # Set the color file
        # ------------------
        self.set_color_file(self.__model_2D_used.get_color_file())
