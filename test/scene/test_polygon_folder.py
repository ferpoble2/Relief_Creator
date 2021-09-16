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
File with tests  related to the folders of polygons showed on the GUI.
"""
import unittest

from src.program.program import Program


class TestPolygonFolderCreation(unittest.TestCase):

    def setUp(self) -> None:
        """
        Logic executed at the beginning of every test.

        Create the variables necessary to check the logic of the program.
        """
        self.program = Program()
        self.engine = self.program.engine
        self.gui_manager = self.engine.gui_manager

    def tearDown(self) -> None:
        """
        Delete all temporary files created by the program on the setup or testing processes.

        Returns: None
        """
        self.program.close()

    def test_create_folder(self):
        folder_list = self.gui_manager.get_polygon_folder_id_list()
        self.assertEqual([], folder_list, 'List is not empty at the beginning.')

        folder_1_id = self.gui_manager.create_polygon_folder('folder_1')
        folder_list = self.gui_manager.get_polygon_folder_id_list()
        self.assertEqual([folder_1_id], folder_list, 'Folder must have only one folder.')

        folder_2_id = self.gui_manager.create_polygon_folder('folder_2')
        folder_list = self.gui_manager.get_polygon_folder_id_list()
        self.assertEqual([folder_1_id, folder_2_id], folder_list, 'Folder must have only one folder.')

        # check the names
        self.assertEqual('folder_1', self.gui_manager.get_polygon_folder_name(folder_1_id),
                         'Folder with id 0 does not have name folder_1')
        self.assertEqual('folder_2', self.gui_manager.get_polygon_folder_name(folder_2_id),
                         'Folder with id 1 does not have name folder_2')

    def test_delete_folder(self):
        folder_0_id = self.gui_manager.create_polygon_folder('folder_0')
        folder_1_id = self.gui_manager.create_polygon_folder('folder_1')
        folder_2_id = self.gui_manager.create_polygon_folder('folder_2')

        self.assertEqual([folder_0_id, folder_1_id, folder_2_id], self.gui_manager.get_polygon_folder_id_list(),
                         'ID list is not [0, 1, 2].')

        self.gui_manager.delete_polygon_folder(folder_1_id)
        self.assertEqual([folder_0_id, folder_2_id], self.gui_manager.get_polygon_folder_id_list(),
                         'ID list is not [0, 2].')

        self.gui_manager.delete_polygon_folder(folder_0_id)
        self.assertEqual([folder_2_id], self.gui_manager.get_polygon_folder_id_list(), 'ID list is not [2].')

        self.gui_manager.delete_polygon_folder(folder_2_id)
        self.assertEqual([], self.gui_manager.get_polygon_folder_id_list(), 'ID list must be empty.')

    def test_add_polygon_to_folder(self):
        folder_0_id = self.gui_manager.create_polygon_folder('folder_0')
        polygon_id = self.engine.create_new_polygon()

        self.gui_manager.add_polygon_to_gui(polygon_id, folder_0_id)
        self.assertEqual([polygon_id], self.gui_manager.get_polygons_id_from_polygon_folder(folder_0_id),
                         'Folder does not have the ID of the added polygon.')

        polygon_id_2 = self.engine.create_new_polygon()
        self.gui_manager.add_polygon_to_gui(polygon_id_2, folder_0_id)
        self.assertEqual([polygon_id, polygon_id_2], self.gui_manager.get_polygons_id_from_polygon_folder(folder_0_id),
                         'Folder does not have the ID of the added polygon.')

        polygon_id_3 = self.engine.create_new_polygon()
        self.gui_manager.add_polygon_to_gui(polygon_id_3, folder_0_id)
        self.assertEqual([polygon_id, polygon_id_2, polygon_id_3],
                         self.gui_manager.get_polygons_id_from_polygon_folder(folder_0_id),
                         'Folder does not have the ID of the added polygon.')

    def test_remove_polygon_from_folder(self):
        folder_0_id = self.gui_manager.create_polygon_folder('folder_0')
        polygon1_id = self.engine.create_new_polygon()
        polygon2_id = self.engine.create_new_polygon()
        polygon3_id = self.engine.create_new_polygon()

        self.gui_manager.add_polygon_to_gui(polygon1_id, folder_0_id)
        self.gui_manager.add_polygon_to_gui(polygon2_id, folder_0_id)
        self.gui_manager.add_polygon_to_gui(polygon3_id, folder_0_id)

        self.assertEqual([polygon1_id, polygon2_id, polygon3_id],
                         self.gui_manager.get_polygons_id_from_polygon_folder(folder_0_id),
                         'Folder does not have the polygons added.')

        self.gui_manager.delete_polygon_by_id(polygon1_id)
        self.assertEqual([polygon2_id, polygon3_id],
                         self.gui_manager.get_polygons_id_from_polygon_folder(folder_0_id),
                         'Polygon not deleted from the folder.')

        self.gui_manager.delete_polygon_by_id(polygon3_id)
        self.assertEqual([polygon2_id],
                         self.gui_manager.get_polygons_id_from_polygon_folder(folder_0_id),
                         'Polygon not deleted from the folder.')

        self.gui_manager.delete_polygon_by_id(polygon2_id)
        self.assertEqual([],
                         self.gui_manager.get_polygons_id_from_polygon_folder(folder_0_id),
                         'Polygon not deleted from the folder.')

    def test_remove_all_polygons_from_folder(self):
        folder_0_id = self.gui_manager.create_polygon_folder('folder_0')
        polygon1_id = self.engine.create_new_polygon()
        polygon2_id = self.engine.create_new_polygon()
        polygon3_id = self.engine.create_new_polygon()

        self.gui_manager.add_polygon_to_gui(polygon1_id, folder_0_id)
        self.gui_manager.add_polygon_to_gui(polygon2_id, folder_0_id)
        self.gui_manager.add_polygon_to_gui(polygon3_id, folder_0_id)

        self.assertEqual([polygon1_id, polygon2_id, polygon3_id],
                         self.gui_manager.get_polygons_id_from_polygon_folder(folder_0_id),
                         'Folder does not have the polygons added.')

        self.gui_manager.delete_all_polygons_inside_folder(folder_0_id)
        self.assertEqual([],
                         self.gui_manager.get_polygons_id_from_polygon_folder(folder_0_id),
                         'Polygons not deleted from the folder.')
