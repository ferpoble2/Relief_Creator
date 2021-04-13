"""
File with the definition of the class Map3DModel, class in charge of the 3D representation of the maps.
"""
import numpy as np

from src.engine.scene.model.model import Model

from src.type_hinting import *


class Map3DModel(Model):
    """
    Class that manage all things related to the representation in 3D of the maps.
    """

    def __init__(self, scene: 'Scene', model_2d: 'Map2DModel'):
        """
        Constructor of the class.
        """
        super().__init__(scene)

        self.set_shaders("./engine/shaders/simple_vertex.glsl",
                         "./engine/shaders/simple_fragment.glsl")

        # TODO: delete this and use the data from the Map2Dmodel
        self.set_vertices(np.array([0, 0, 0, 1, 0, 0, 0, 1, 0]))
        self.set_indices(np.array([0, 1, 2]))

        # self.set_vertices(model_2d.get_vertices_array())
        # self.set_indices(model_2d.get_indices_array())

    def _update_uniforms(self) -> None:
        """
        Method to update the uniforms used in the shader programs.

        Returns: None
        """
        pass
