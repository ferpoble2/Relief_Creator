"""
File that contain the Scene class. This class is in charge of the management of the models of the scene.
"""
from typing import List

from src.engine.model.map2dmodel import Map2DModel
from src.engine.model.model import Model
from src.input.NetCDF import read_info
from src.utils import get_logger

log = get_logger(module="SCENE")


class Scene:

    def __init__(self):
        """
        Constructor of the class.
        """
        self.__model_list: List[Model] = []

    def draw(self) -> None:
        """
        Draw the models in the list.

        Draw the models in the order of the list.
        Returns: None
        """
        for model in self.__model_list:
            model.draw()

    def add_model(self, model: Model) -> None:
        """
        Add a model to the list of models.
        Args:
            model: Model to add to the list

        Returns: None
        """
        self.__model_list.append(model)

    def remove_all_models(self) -> None:
        """
        Remove all models from the list of models.
        Returns: None
        """
        self.__model_list = []

    def remove_model(self, id_model: str) -> None:
        """
        Return the model with the specified id.
        Args:
            id_model: Id of the model to remove.

        Returns: None
        """
        model_to_remove = None
        for model in self.__model_list:
            if model.id == id_model:
                model_to_remove = model

        self.__model_list.remove(model_to_remove)

    def set_polygon_mode(self, polygon_mode) -> None:
        """
        Select if the models uses the wireframe mode or not.
        Args:
            polygon_mode: OpenGL polygon mode to draw the model.

        Returns: None
        """
        for model in self.__model_list:
            model.polygon_mode = polygon_mode

    def refresh_with_model_2d(self, path_color_file: str, path_model: str) -> None:
        """
        Refresh the scene, removing all the models, and adding the new model specified
        in the input.

        The model added will be added as a 2d model to the program.

        The model must  be in netCDF format.

        The color file must be in CTP format.

        Args:
            path_color_file: Path to the CTP file with the colors.
            path_model: Path to the

        Returns:

        """

        if path_model is not None and path_color_file is not None:
            log.debug("Reading information from file.")
            X, Y, Z = read_info(path_model)

            log.debug("Generating model")
            model = Map2DModel()

            log.debug("Setting vertices from grid.")
            model.set_vertices_from_grid(X, Y, Z, 3)

            log.debug("Settings colors from file.")
            model.set_color_file(path_color_file)
            model.wireframes = False

            # SCENE CODE
            # ----------
            self.remove_all_models()
            self.add_model(model)