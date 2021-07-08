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
File that will contain the class PolygonFolder, class in charge of the functionality related to the folders
of polygons.
"""


class PolygonFolder:
    """
    Class in charge of the management of the folders of the polygons.
    """

    def __init__(self, folder_id: str):
        self.__id = folder_id
        self.__name = 'folder'
        self.__polygon_id_list = []

    def add_polygon(self, polygon_id: str) -> None:
        """
        Add a polygon to the folder.

        Args:
            polygon_id: ID of the new polygon

        Returns: None
        """
        self.__polygon_id_list.append(polygon_id)

    def delete_polygon(self, polygon_id: str) -> None:
        """
        Delete the polygon from the list of polygons.

        Args:
            polygon_id: Delete the polygon from the list of polygons.

        Returns: None
        """
        if polygon_id in self.__polygon_id_list:
            self.__polygon_id_list.remove(polygon_id)

    def get_id(self) -> str:
        """
        Get the ID of the folder.

        Returns: ID of the folder.
        """
        return self.__id

    def get_name(self) -> str:
        """
        Get the name of the polygon folder.

        Returns: Name of the polygon folder.
        """
        return self.__name

    def get_polygon_list(self) -> list:
        """
        Get the polygon list.

        Returns: List with the polygon ID of the polygons on the folder.
        """
        return self.__polygon_id_list

    def set_name(self, new_name: str) -> None:
        """
        Set the name of the polygon folder.

        Returns: None
        """
        self.__name = new_name

    def move_polygon(self, polygon_id: str, movement_offset: int) -> None:
        """
        Move the polygon position within the list of polygons stored.

        Examples:

            If the folder contains the following polygons:

                [polygon_1, polygon_2, polygon_3, polygon_4]

            then using movement_offset equal to -2 to move the polygon_4 will result in the folder containing the
            polygons in the following order:

                [polygon_1, polygon_4, polygon_2, polygon_3]

        Args:
            polygon_id: ID of the polygon to move.
            movement_offset: How much to move the polygon inside the folder.

        Returns: None
        """
        if polygon_id not in self.__polygon_id_list:
            raise KeyError(f'Polygon {polygon_id} is not in the folder {self.__name} with id {self.__id}.')

        curr_index = self.__polygon_id_list.index(polygon_id)
        target_index = curr_index + movement_offset

        self.__polygon_id_list.remove(polygon_id)
        self.__polygon_id_list.insert(target_index, polygon_id)
