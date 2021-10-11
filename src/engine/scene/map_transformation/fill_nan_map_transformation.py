#  BEGIN GPL LICENSE BLOCK
#
#      This program is free software: you can redistribute it and/or modify
#      it under the terms of the GNU General Public License as published by
#      the Free Software Foundation, either version 3 of the License, or
#      (at your option) any later version.
#
#      This program is distributed in the hope that it will be useful,
#      but WITHOUT ANY WARRANTY; without even the implied warranty of
#      MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#      GNU General Public License for more details.
#
#      You should have received a copy of the GNU General Public License
#      along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
#  END GPL LICENSE BLOCK

"""
Module that defines the FillNanMapTransformation class. Class in charge of filling with nan the height of the points
at the interior of all the polygons loaded into the scene.
"""
from typing import Dict, List, TYPE_CHECKING

import numpy as np
from shapely.geometry import LinearRing

from engine.scene.geometrical_operations import delete_z_axis, generate_mask, get_bounding_box_indexes
from src.engine.scene.map_transformation.map_transformation import MapTransformation
from src.error.map_transformation_error import MapTransformationError

if TYPE_CHECKING:
    from src.engine.scene.scene import Scene


class FillNanMapTransformation(MapTransformation):
    """
    Class in charge of the  transformation that fills with nan the height of the points that are at the interior of the
    polygons defined on the program.
    """

    def __init__(self, model_to_modify: str):
        super().__init__(model_to_modify)

        self.__polygon_points: Dict[str, List[float]] = {}
        self.__model_vertices: np.ndarray = np.array([])

    def initialize(self, scene: 'Scene') -> None:
        """
        Get the information of the polygons that are loaded into the program and the information of the vertices of the
        model.

        Args:
            scene: Scene to use to get the data.

        Returns: None
        """
        super().initialize(scene)

        # Get the information of the polygons
        # -----------------------------------
        model_id_list = scene.get_model_list()
        if self.model_id not in model_id_list:
            raise MapTransformationError(1)

        self.__model_vertices = scene.get_map2d_model_vertices_array(self.model_id)

        # Get the information of the polygons
        # -----------------------------------
        polygon_id_list = scene.get_polygon_id_list()
        for polygon_id in polygon_id_list:
            if not scene.is_polygon_planar(polygon_id):
                raise MapTransformationError(2)

            self.__polygon_points[polygon_id] = scene.get_polygon_points(polygon_id)

    def apply(self) -> np.ndarray:
        """
        Fill with nan the heights of the points at the interior of the polygons loaded into the program.

        Returns: Array of the vertices of the modified model.
        """
        points_array = self.__model_vertices
        height = self.__model_vertices[:, :, 2]

        for polygon_id, polygon_points in self.__polygon_points.items():

            # Do nothing if polygon does not have enough points
            # -------------------------------------------------
            if len(polygon_points) < 9:
                continue

            # Generate polygon and get the bounding box of the indices
            # --------------------------------------------------------
            points_no_z_axis = delete_z_axis(polygon_points)
            closed_polygon = LinearRing(points_no_z_axis)
            [min_x_index, max_x_index, min_y_index, max_y_index] = get_bounding_box_indexes(points_array,
                                                                                            closed_polygon)

            points_array_cut = points_array[min_y_index:max_y_index, min_x_index:max_x_index, :]
            height_cut = height[min_y_index:max_y_index, min_x_index:max_x_index]

            # Do nothing in case that no points from the map are selected
            # -----------------------------------------------------------
            if len(points_array_cut) == 0:
                continue

            # Generate mask for the points
            # ----------------------------
            flags = generate_mask(points_array_cut, polygon_points)

            # Set nan to the height values
            # ----------------------------
            if len(height_cut[flags]) > 0:
                height_cut[flags] = np.nan
                height[min_y_index:max_y_index, min_x_index:max_x_index] = height_cut

        return self.__model_vertices
