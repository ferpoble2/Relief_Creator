"""
File that will contain the class PolygonFolder, class in charge of the functionality related to the folders
of polygons.
"""


class PolygonFolder:
    """
    Class in charge of the management of the folders of the polygons.
    """

    def __init__(self, id: str):
        self.__id = id
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

    def get_polygon_list(self) -> list:
        """
        Get the polygon list.

        Returns: List with the polygon ID of the polygons on the folder.
        """
        return self.__polygon_id_list
