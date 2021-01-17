"""
File containing the class polygon.

This class stores all the information related to the polygons that can be draw on the screen of the program.
"""
from src.engine.scene.model.model import Model

import numpy as np
import OpenGL.GL as GL


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

        self.update_uniform_values = False

        # Polygon variables
        # ------------------
        self.__point_list = []
        self.__indices_list = []

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

    def get_id(self) -> str:
        """
        Get the id of the polygon.

        Returns: Id of the polygon
        """
        return self.id

    def set_id(self, new_id: str) -> None:
        """
        Set a new id for the polygon.

        Args:
            new_id: New ID of the polygon.

        Returns: None
        """
        self.id = new_id

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

    def draw(self) -> None:
        """
        Set how and when to draw the polygons.
        """
        if self.get_point_number() > 1:
            super().draw()

    def generate_initial_indices(self) -> None:
        """
        Generate the initial configuration of indices on the indices list.

        Returns: None
        """
        self.__indices_list.append(0)
        self.__indices_list.append(1)

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
