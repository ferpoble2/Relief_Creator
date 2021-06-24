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
File that contains the definition of the PoligonManager class, class in charge of the management of the
folders of polygonfolder.
"""
from typing import Dict

from src.engine.GUI.polygon_folder import PolygonFolder
from src.error.polygon_folder_not_found_error import PolygonFolderNotFoundError


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

    def add_polygon_to_imported_polygon_folder(self, polygon_id: str) -> None:
        """
        Add the polygon to the imported polygon folder. It creates the folder if it does not exist.

        Args:
            polygon_id: ID of the polygon to add.

        Returns: None
        """
        if 'imported_polygons' not in self.__folders:
            folder = PolygonFolder('imported_polygons')
            folder.set_name('Imported Polygons')
            self.__folders[folder.get_id()] = folder

        self.add_polygon_to_folder('imported_polygons', polygon_id)

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
            raise PolygonFolderNotFoundError('Polygon Folder not found in the program.')

        self.__folders[folder_id] = []

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
            raise PolygonFolderNotFoundError('Folder is not in the dictionary of folders.')

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
            raise PolygonFolderNotFoundError('Polygon Folder not found in the program.')

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
            raise PolygonFolderNotFoundError('Folder is not in the dictionary of folders.')

        return folder.get_name()

    def get_polygon_id_list(self, folder_id: str) -> list:
        """
        Get the list of polygons ids inside a folder.

        Returns: list with the list of polygons id inside the folder.

        Args:
            folder_id (object): id of the folder.
        """
        folder = self.__folders.get(folder_id)

        if folder is None:
            raise PolygonFolderNotFoundError('Folder is not in the dictionary of folders.')

        return folder.get_polygon_list()

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
            new_name: new namo for the folder.

        Returns: None
        """
        folder = self.__folders.get(folder_id)
        if folder is None:
            raise PolygonFolderNotFoundError('Folder is not in the dictionary of folders.')

        folder.set_name(new_name)
