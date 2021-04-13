"""
File with the definition of the class Map3DModel, class in charge of the 3D representation of the maps.
"""
import numpy as np
import OpenGL.GL as GL

from src.engine.scene.model.model import Model
from src.engine.scene.model.tranformations.transformations import lookAt, perspective, rotationA, translate, identity

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

        self.set_shaders("./engine/shaders/model_3d_vertex.glsl",
                         "./engine/shaders/model_3d_fragment.glsl")

        self.__model = identity()
        self.__view = self.scene.get_camera_view_matrix()

        # TODO: obtener toda esta informacion de los settings.
        scene_settings_data = self.scene.get_scene_setting_data()
        camera_settings_data = self.scene.get_camera_settings()
        self.__projection = perspective(camera_settings_data['FIELD_OF_VIEW'],
                                        scene_settings_data['SCENE_WIDTH_X'] / scene_settings_data['SCENE_HEIGHT_Y'],
                                        camera_settings_data['PROJECTION_NEAR'],
                                        camera_settings_data['PROJECTION_FAR'])

        # TODO: delete this and use the data from the Map2Dmodel
        self.set_vertices(np.array([0, 0, 0, 1, 0, 0, 0, 1, 0]))
        self.set_indices(np.array([0, 1, 2]))

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
        GL.glUniformMatrix4fv(view_location, 1, GL.GL_TRUE, self.__view)
        GL.glUniformMatrix4fv(projection_location, 1, GL.GL_TRUE, self.__projection)

    def draw(self) -> None:
        """
        Draw the model on the screen.

        Returns: None
        """

        # update the variables
        self.__view = self.scene.get_camera_view_matrix()

        # draw
        super().draw()
