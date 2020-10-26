"""
Class in charge of managing the models of the maps in 2 dimentions.
"""

from src.engine.model.model import Model

class Map2DModel(Model):
    """
    Class that manage all things related to the 2D representation of the maps.
    """

    def set_vertices_from_grid(self, x, y, z):
        """
        Set the vertices of the model from a grid.

        Args:
            x: X values of the grid to use.
            y: Y values of the grid.
            z: Z values of the grid.

        Returns: None

        """

        # TODO: Create function to determinate position of the vertex depending of the screen.

