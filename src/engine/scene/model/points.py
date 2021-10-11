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
File with the class Points, class in charge of storing all the information related to the models that draw points on
the scene
"""
import ctypes as ctypes

import OpenGL.GL as GL
import numpy as np

from src.engine.scene.model.model import Model
from src.utils import get_logger

log = get_logger(module="POINTS")


class Points(Model):
    """
    Class in charge of the modeling of points in the program.
    """

    def __init__(self, scene, point_list: np.ndarray = None):
        """
        Constructor of the class.

        A list of points can be optionally passed to the constructor to create a model with already initialized points.
        The list of points must be an array of shape (num_points, 3), with each row being a point of the model.

        Args:
            point_list: List of points to use as initial value. This array will not be modified.
                        Format of the array must be [[x, y, z], [x, y, z], ...]
        """
        super().__init__(scene)

        # Properties of the model
        # -----------------------
        self.cbo = GL.glGenBuffers(1)
        self.draw_mode = GL.GL_POINTS
        self.update_uniform_values = False

        self.__vertex_shader_file = './src/engine/shaders/point_vertex.glsl'
        self.__fragment_shader_file = './src/engine/shaders/point_fragment.glsl'

        # Data of the points
        # ------------------
        self.__point_list = []
        self.__indices_list = []
        self.__color_list = []
        self.__normal_color = (1, 1, 0, 1)  # RGBA
        self.__first_point_color = (1, 0, 0, 1)  # RGBA
        self.__last_point_color = (0, 0, 1, 1)  # RGBA

        self.set_shaders(self.__vertex_shader_file, self.__fragment_shader_file)

        # Initialize model if data is given
        # ---------------------------------
        if point_list is not None:
            point_list_copy = point_list.copy()

            # Set points
            # ----------
            self.__point_list = list(point_list.reshape(-1))
            self.set_vertices(np.array(self.__point_list, dtype=np.float32))

            point_number = len(point_list_copy)
            assert point_number > 0, 'Trying to load points with an array with no data.'

            # Set colors
            # ----------
            if point_number == 1:
                self.__color_list = list(self.__first_point_color)
            elif point_number == 2:
                self.__color_list = list(self.__first_point_color) + list(self.__last_point_color)
            elif point_number > 2:
                self.__color_list = list(self.__first_point_color) + list(self.__normal_color) * (point_number - 2) + \
                                    list(self.__last_point_color)
            self.set_color_buffer(np.array(self.__color_list, dtype=np.float32))

            # Set indices
            # -----------
            self.__indices_list = list(range(point_number))
            self.set_indices(np.array(self.__indices_list, dtype=np.uint32))

    def __add_color_to_color_list(self, color: tuple) -> None:
        """
        Add a color to the color list.

        Args:
            color: New color to add (must have 4 elements)

        Returns: None
        """
        if len(color) < 4:
            raise AssertionError("Trying to add a color with fewer than 4 components.")

        self.__color_list.append(color[0])
        self.__color_list.append(color[1])
        self.__color_list.append(color[2])
        self.__color_list.append(color[3])

    def __remove_last_color_from_color_list(self) -> None:
        """
        Remove the last color from the color list.

        Returns: None
        """
        if len(self.__color_list) >= 4:
            self.__color_list.pop()
            self.__color_list.pop()
            self.__color_list.pop()
            self.__color_list.pop()

    def __remove_last_point_from_point_list(self) -> None:
        """
        Remove the last point from the list of points.

        Returns: None
        """
        if len(self.__point_list) >= 3:
            self.__point_list.pop()
            self.__point_list.pop()
            self.__point_list.pop()

    def __str__(self) -> str:
        """
        Return the string representing the object.

        Returns: string representing the object.
        """
        string_to_print = f"Points model data:\n"

        points = np.array(self.__point_list).reshape((-1, 3))
        colors = np.array(self.__color_list).reshape((-1, 4))
        for index in range(len(points)):
            string_to_print += f"Index: {index} - coordinates: {points[index]} - color: {colors[index]}"
            string_to_print += "\n"

        string_to_print += f"\nIndices list: {self.__indices_list}"
        string_to_print += f"\nPoint list: {self.__point_list}"
        string_to_print += f"\nColor list: {self.__color_list}"

        return string_to_print

    def _update_uniforms(self) -> None:
        """
        Update the uniforms values for the model.

        Returns: None
        """

        # Update values for the polygon shader
        # ------------------------------------
        projection_location = GL.glGetUniformLocation(self.shader_program, "projection")

        # Set the color and projection matrix to use
        # ------------------------------------------
        GL.glUniformMatrix4fv(projection_location, 1, GL.GL_TRUE, self.scene.get_projection_matrix_2D())

    def add_point(self, x: float, y: float, z: float) -> None:
        """
        Add a point to the list to draw

        Args:
            x: x position of the point
            y: y position of the point
            z: z position of the point

        Returns: None
        """

        # Update the vertices buffer
        # --------------------------
        self.__point_list.append(x)
        self.__point_list.append(y)
        self.__point_list.append(z)
        self.set_vertices(np.array(self.__point_list, dtype=np.float32))

        # Update the color buffer
        # -----------------------
        if len(self.__color_list) / 4 == 0:
            self.__add_color_to_color_list(self.__first_point_color)

        elif len(self.__color_list) / 4 == 1:
            self.__add_color_to_color_list(self.__last_point_color)

        else:
            self.__remove_last_color_from_color_list()
            self.__add_color_to_color_list(self.__normal_color)
            self.__add_color_to_color_list(self.__last_point_color)

        self.set_color_buffer(np.array(self.__color_list, dtype=np.float32))

        # Update the indices buffer
        # -------------------------
        self.__indices_list.append(len(self.__point_list) / 3 - 1)
        self.set_indices(np.array(self.__indices_list, dtype=np.uint32))

    def draw(self) -> None:
        """
        Draw the points on the scene

        Returns: None
        """

        # draw if there is at least one point
        if len(self.__point_list) / 3 > 0:
            # get the settings of the points to draw
            render_settings = self.scene.get_render_settings()
            dot_size = render_settings["DOT_SIZE"]
            polygon_dot_size = render_settings["POLYGON_DOT_SIZE"]

            # draw the points
            GL.glPointSize(polygon_dot_size)
            super().draw()
            GL.glPointSize(dot_size)

    def get_first_point_color(self) -> tuple:
        """
        get the color to use in the drawing of the first point

        Returns: tuple with the color in rgb format
        """
        return self.__first_point_color

    def get_last_point_color(self) -> tuple:
        """
        get the color to use in the drawing of the last point

        Returns: tuple with the color in rgb format
        """
        return self.__last_point_color

    def get_normal_color(self) -> tuple:
        """
        get the normal color to use in the drawing of the points

        Returns: tuple with the color in rgb format
        """
        return self.__normal_color

    def get_point_list(self) -> list:
        """
        Get the point list.
        The format of the list is as follows: [x1, y1, z1, x2, y2, z2, ...]

        Returns: Point list
        """
        return self.__point_list

    def remove_last_added_point(self) -> None:
        """
        Remove the last added point to the list of points.

        This update the buffers in the GPU

        Returns: None
        """

        # only works when there is one point or more
        if len(self.__point_list) / 3 > 0:

            # remove the last point
            self.__remove_last_point_from_point_list()

            # remove the index representing the old last point
            if len(self.__indices_list) > 0:
                self.__indices_list.pop()

            # remove the color of the removed point and change the color of the new last point
            self.__remove_last_color_from_color_list()

            # only change color if there is more than one point in the list
            if len(self.__point_list) / 3 > 1:
                self.__remove_last_color_from_color_list()
                self.__add_color_to_color_list(self.__last_point_color)

            # update the buffers on the GPU
            self.set_vertices(np.array(self.__point_list, dtype=np.float32))
            self.set_color_buffer(np.array(self.__color_list, dtype=np.float32))
            self.set_indices(np.array(self.__indices_list, dtype=np.uint32))

        log.debug(self)

    def set_color_buffer(self, colors: np.ndarray) -> None:
        """
        Set the color buffer in opengl with the colors of the array

        Args:
            colors: Colors to use in the buffer

        Returns: None
        """
        GL.glBindVertexArray(self.vao)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.cbo)
        GL.glBufferData(
            GL.GL_ARRAY_BUFFER,
            len(colors) * self.scene.get_float_bytes(),
            colors,
            GL.GL_STATIC_DRAW
        )
        GL.glVertexAttribPointer(
            1, 4, GL.GL_FLOAT, GL.GL_FALSE, 0, ctypes.c_void_p(0)
        )
        GL.glEnableVertexAttribArray(1)

    def set_first_point_color(self, new_color: tuple) -> None:
        """
        Set the color to use to coloring the first point.

        Args:
            new_color: New color to use for the first point. (R, G, B)

        Returns: None
        """
        self.__first_point_color = new_color

        # update the color buffer if there is at least one point defined
        if len(self.__point_list) / 3 > 0:
            self.__color_list[0] = new_color[0]
            self.__color_list[1] = new_color[1]
            self.__color_list[2] = new_color[2]
            self.__color_list[3] = new_color[3]

            self.set_color_buffer(np.array(self.__color_list, dtype=np.float32))

    def set_last_point_color(self, new_color: tuple) -> None:
        """
        Set the color to use in the last point

        Args:
            new_color: New color to use in the last point. (R, G, B)

        Returns: None
        """
        self.__last_point_color = new_color

        # update the color buffer if there is at least two point defined
        if len(self.__point_list) / 3 > 1:
            self.__color_list.pop()
            self.__color_list.pop()
            self.__color_list.pop()
            self.__color_list.pop()

            self.__color_list.append(new_color[0])
            self.__color_list.append(new_color[1])
            self.__color_list.append(new_color[2])
            self.__color_list.append(new_color[3])

            self.set_color_buffer(np.array(self.__color_list, dtype=np.float32))

    def set_normal_color(self, new_color: tuple) -> None:
        """
        Set the normal color to use to coloring the points.

        Args:
            new_color: New color to use. (R, G, B)

        Returns: None
        """
        self.__normal_color = new_color

        # update the color buffer if there is at least three points defined
        if len(self.__point_list) / 3 > 2:
            number_of_point = int(len(self.__point_list) / 3)

            self.__color_list = []

            # append the initial color
            self.__color_list.append(self.__first_point_color[0])
            self.__color_list.append(self.__first_point_color[1])
            self.__color_list.append(self.__first_point_color[2])
            self.__color_list.append(self.__first_point_color[3])

            # append the new color to the list
            for _ in range(number_of_point - 2):
                self.__color_list.append(self.__normal_color[0])
                self.__color_list.append(self.__normal_color[1])
                self.__color_list.append(self.__normal_color[2])
                self.__color_list.append(self.__normal_color[3])

            # append the last color
            self.__color_list.append(self.__last_point_color[0])
            self.__color_list.append(self.__last_point_color[1])
            self.__color_list.append(self.__last_point_color[2])
            self.__color_list.append(self.__last_point_color[3])

            # update the color buffer
            self.set_color_buffer(np.array(self.__color_list, dtype=np.float32))
