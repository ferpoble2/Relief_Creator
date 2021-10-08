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
File that contains the definition of the PolygonManager class, class in charge of the management of the
folders of the GUI.
"""
from typing import Dict

from src.engine.GUI.polygon_folder import PolygonFolder
from src.error.polygon_folder_error import PolygonFolderError


class PolygonFolderManager:
    """
    Class in charge of the management of the folders of polygons.
    """

    def __init__(self):
        """
        Constructor of the class
        """
        self.__folder_count_id = 0
        self.__folders: Dict[str, PolygonFolder] = {}

    def __create_new_folder(self, name='new_folder') -> PolygonFolder:
        """
        Create a new folder and modify the corresponding internal variables.
        Returns: Folder created
        """
        folder = PolygonFolder(str(self.__folder_count_id))
        folder.set_name(name)
        self.__folder_count_id += 1
        self.__folders[folder.get_id()] = folder
        return folder

    def add_polygon_to_folder(self, folder_id: str, polygon_id: str) -> None:
        """
        Add a new polygon to the folder.

        Args:
            folder_id: Folder to add the new polygon. (create it if doesnt exist)
            polygon_id: polygon_id to add

        Returns: None
        """
        folder = self.__folders.get(folder_id)

        if folder is None:
            folder = self.__create_new_folder()

        folder.add_polygon(polygon_id)

    def get_polygon_position(self, polygon_id: str) -> int:
        """
        Return the polygon position in the list of all the polygons that are inside all the folders.

        If there is three folders of polygons as follows:
            Folder 1
                polygon 1
                polygon 2

            Folder 2

            Folder 3
                polygon 3

        Then this method generate the list [polygon 1, polygon 2, polygon 3] and return the index of the element
        specified on the parameters.

        Args:
            polygon_id: ID of the polygon to search.

        Returns: Index of the polygon in the list containing all the polygons on all the folders.
        """
        polygons = []
        for folder in self.__folders.values():
            polygons += folder.get_polygon_list()

        return polygons.index(polygon_id)

    def get_imported_polygon_folder_id(self) -> str:
        """
        Get the id of the folder that stores all the imported polygons.

        If the folder does not exist, this method creates it.

        Returns: ID of the imported polygon folder.
        """

        # create folder if not exist
        if 'imported_polygons' not in self.__folders:
            folder = PolygonFolder('imported_polygons')
            folder.set_name('Imported Polygons')
            self.__folders[folder.get_id()] = folder

        return 'imported_polygons'

    def create_new_folder(self, name='new_folder') -> str:
        """
        Creates a new folder.

        Returns: ID of the created folder.
        """
        folder = self.__create_new_folder(name)
        return folder.get_id()

    def delete_all_polygons_inside_folder(self, folder_id: str) -> None:
        """
        Delete all polygons inside the folder.

        Args:
            folder_id: ID of the folder.

        Returns: None
        """
        folder = self.__folders.get(folder_id)

        if folder is None:
            raise PolygonFolderError(0)

        self.__folders[folder_id] = PolygonFolder(folder_id=folder_id)

    def delete_folder(self, folder_id: str) -> None:
        """
        Delete the folder from the dictionary of folders.

        Args:
            folder_id: folder to delete

        Returns: None
        """
        if folder_id in self.__folders:
            self.__folders.pop(folder_id)

        else:
            raise PolygonFolderError(0)

    def delete_polygon_from_all_folders(self, polygon_id: str) -> None:
        """
        Delete the specified polygon from all the folders.

        Args:
            polygon_id: ID of the polygon to delete.

        Returns: None
        """
        for folder in list(self.__folders.values()):
            folder.delete_polygon(polygon_id)

    def delete_polygon_inside_folder(self, polygon_id: str, folder_id: str) -> None:
        """
        Delete a polygon inside a specified folder.

        Args:
            polygon_id: polygon id
            folder_id: folder id

        Returns: None
        """
        folder = self.__folders.get(folder_id)

        if folder is None:
            raise PolygonFolderError(0)

        folder.delete_polygon(polygon_id)

    def get_folder_id_list(self) -> list:
        """
        Return the list of IDs of all the folders.

        Returns: List with the ids of the folders.
        """
        return list(self.__folders.keys())

    def get_name_of_folder(self, folder_id: str) -> str:
        """
        Get the name of a folder.

        Args:
            folder_id: Folder to get the name

        Returns: Name of the folder
        """
        folder = self.__folders.get(folder_id)
        if folder is None:
            raise PolygonFolderError(0)

        return folder.get_name()

    def get_polygon_id_list(self, folder_id: str = None) -> list:
        """
        Get the list of polygons ids inside a folder.

        If no folder specified, get a list of all the polygon IDs from all the folders.

        Args:
            folder_id: ID of the folder.

        Returns: list with the list of polygons id inside the folder.
        """
        if folder_id is not None:
            folder = self.__folders.get(folder_id)
            if folder is None:
                raise PolygonFolderError(0)

            return folder.get_polygon_list()

        else:
            polygon_id = []
            for folder in self.__folders.values():
                polygon_id += folder.get_polygon_list()
            return polygon_id

    def move_polygon_to_folder(self, old_folder_id: str, polygon_id: str, folder_id: str) -> None:
        """
        Moves the polygon from one folder to another

        Args:
            old_folder_id: id of the old folder
            polygon_id: id of the polygon to move
            folder_id: id of the destination folder

        Returns: None
        """
        self.delete_polygon_inside_folder(polygon_id, old_folder_id)
        self.add_polygon_to_folder(folder_id, polygon_id)

    def set_name_of_folder(self, folder_id: str, new_name: str) -> None:
        """
        Change the name of a folder.

        Args:
            folder_id: ID of the folder.
            new_name: new name for the folder.

        Returns: None
        """
        folder = self.__folders.get(folder_id)
        if folder is None:
            raise PolygonFolderError(0)

        folder.set_name(new_name)

    def move_polygon_position(self, polygon_folder_id: str, polygon_id: str, movement_offset: int) -> None:
        """
        Move the position of a polygon inside the folder that contain itself.

        This changes the order in which the polygons are returned when asked for the list of polygons inside the
        specified folder.

        Examples:
            If the folder contains the following polygons:

                [polygon_1, polygon_2, polygon_3, polygon_4]

            then using movement_offset equal to -2 to move the polygon_4 will result in the folder containing the
            polygons in the following order:

                [polygon_1, polygon_4, polygon_2, polygon_3]

        Args:
            polygon_folder_id: ID of the folder where the polygon is located.
            polygon_id: ID of the polygon to move.
            movement_offset: How many positions to move the polygon.

        Returns: None
        """
        # Move the position of the polygon
        self.__folders[polygon_folder_id].move_polygon(polygon_id, movement_offset)

    def move_folder_position(self, polygon_folder_id, movement_offset):
        """
        Move the position of the folders on the internal structure.

        This method affect the order when the folders are retrieved using the method get_folder_id_list.

        Example:
            If the folders are arranged as follows:

                Folder 1
                Folder 2
                Folder 3

            Then, using a movement_offset of -2 in the Folder 3 will result in this:

                Folder 3
                Folder 2
                Folder 1

        Args:
            polygon_folder_id: ID of the folder to move.
            movement_offset: How much to move the folder.

        Returns: None
        """

        # Get the list of folders and get the index of the folder and the target index
        # ----------------------------------------------------------------------------
        folder_id_list = list(self.__folders.keys())
        curr_index = folder_id_list.index(polygon_folder_id)
        target_index = folder_id_list.index(polygon_folder_id) + movement_offset

        # Get the items of the dictionary and change the order of the elements
        # --------------------------------------------------------------------
        folder_dictionary_items = list(self.__folders.items())

        folder_dictionary_items.pop(curr_index)
        folder_dictionary_items.insert(target_index, (polygon_folder_id, self.__folders[polygon_folder_id]))

        # Reconstruct the dictionary with the values in the modified order
        # ----------------------------------------------------------------
        new_dict = {}
        for v, k in folder_dictionary_items:
            new_dict[v] = k

        self.__folders = new_dict
