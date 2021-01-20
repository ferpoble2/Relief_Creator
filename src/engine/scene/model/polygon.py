"""
File containing the class polygon.

This class stores all the information related to the polygons that can be draw on the screen of the program.
"""
from src.engine.scene.model.model import Model
from src.utils import get_logger

import numpy as np
import OpenGL.GL as GL

log = get_logger(module="SCENE")


class Polygon(Model):
    """
    Class in charge of the polygons of the program.
    """

    def __init__(self, scene, id):
        """
        Constructor of the class.
        """
        super().__init__(scene)

        self.id = id
        self.draw_mode = GL.GL_LINES

        self.update_uniform_values = True

        # Polygon variables
        # ------------------
        self.__point_list = []
        self.__indices_list = []

        self.__polygon_color = (1, 1, 0, 1)
        self.__polygon_point_color = (1, 0, 0, 1)

    def __str__(self):
        """
        Format how polygons are printed on the console.

        Returns: String representing the polygon.
        """
        string_to_print = ""
        points = np.array(self.__point_list).reshape((-1, 3))
        for index in range(len(points)):
            string_to_print += f"Index: {index} - {points[index]}"
            string_to_print += "\n"

        return string_to_print

    def _update_uniforms(self) -> None:
        """
        Update the uniforms values for the model.

        Returns: None
        """
        projection_location = GL.glGetUniformLocation(self.shader_program, "projection")
        polygon_color_location = GL.glGetUniformLocation(self.shader_program, "polygon_color")

        GL.glUniform4f(polygon_color_location,
                       self.__polygon_color[0],
                       self.__polygon_color[1],
                       self.__polygon_color[2],
                       self.__polygon_color[3])
        GL.glUniformMatrix4fv(projection_location, 1, GL.GL_TRUE, self.scene.get_active_model_projection_matrix())

    def set_line_color(self, color: list) -> None:
        """
        Set the color to draw the lines of the polygon.

        The color must be in a list-like object in the order of RGBA with values between 0 and 1.

        Args:
            color: Color to be used by the polygon

        Returns: None
        """
        log.debug(f"Changing polygon color to {color}")
        self.__polygon_color = (color[0],
                                color[1],
                                color[2],
                                color[3])

    def add_point(self, x: float, y: float, z: float = 0.5) -> None:
        """
        Add a new point to the list of points.

        Args:
            x: x position of the point
            y: y position of the point
            z: z position of the point (default to 0.5)

        Returns: None
        """
        self.__point_list.append(x)
        self.__point_list.append(y)
        self.__point_list.append(z)

        if self.get_point_number() > 1:

            # Append the initial indices for the polygon when there is two points
            if len(self.__indices_list) == 0:
                self.generate_initial_indices()

            # change the last vertex to point to the new vertex
            self.__indices_list.pop()
            self.__indices_list.pop()
            self.__indices_list.append(self.get_point_number() - 2)
            self.__indices_list.append(self.get_point_number() - 1)

            # make the last vertex to point to the first
            self.__indices_list.append(self.get_point_number() - 1)
            self.__indices_list.append(0)

            self.set_vertices(np.array(self.__point_list, dtype=np.float32))
            self.set_indices(np.array(self.__indices_list, dtype=np.uint32))

    def draw(self) -> None:
        """
        Set how and when to draw the polygons.
        """
        if self.get_point_number() > 1:
            render_settings = self.scene.get_render_settings()
            line_width = render_settings["LINE_WIDTH"]
            polygon_line_width = render_settings["POLYGON_LINE_WIDTH"]

            GL.glLineWidth(polygon_line_width)
            super().draw()
            GL.glLineWidth(line_width)

    def generate_initial_indices(self) -> None:
        """
        Generate the initial configuration of indices on the indices list.

        Returns: None
        """
        self.__indices_list.append(0)
        self.__indices_list.append(1)

    def get_id(self) -> str:
        """
        Get the id of the polygon.

        Returns: Id of the polygon
        """
        return self.id

    def get_point_list(self) -> list:
        """
        Get the point list used by the polygon.

        Returns: List with the points to use.
        """
        return self.__point_list

    def get_point_number(self) -> int:
        """
        Return the number of points of the polygon.

        Returns: Number of points of the polygon.
        """
        return int(len(self.__point_list) / 3)

    def set_id(self, new_id: str) -> None:
        """
        Set a new id for the polygon.

        Args:
            new_id: New ID of the polygon.

        Returns: None
        """
        self.id = new_id
