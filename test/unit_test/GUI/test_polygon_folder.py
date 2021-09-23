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

import unittest

from src.engine.GUI.polygon_folder import PolygonFolder


class TestPolygonFolderData(unittest.TestCase):

    def test_default_values(self):
        folder = PolygonFolder('testing_folder_id')

        self.assertEqual('testing_folder_id', folder.get_id())
        self.assertEqual('folder', folder.get_name())
        self.assertEqual([], folder.get_polygon_list())

    def test_modify_name(self):
        folder = PolygonFolder('testing_folder')

        folder.set_name('new_folder_name')
        self.assertEqual('new_folder_name', folder.get_name())

    def test_add_remove_polygons(self):
        folder = PolygonFolder('testing_folder')

        # Add polygons and test the polygon lists
        # ---------------------------------------
        folder.add_polygon('polygon_1')
        self.assertEqual(['polygon_1'], folder.get_polygon_list())

        folder.add_polygon('polygon_2')
        self.assertEqual(['polygon_1', 'polygon_2'], folder.get_polygon_list())

        folder.add_polygon('polygon_3')
        self.assertEqual(['polygon_1', 'polygon_2', 'polygon_3'], folder.get_polygon_list())

        # Remove polygons and tests the list
        # ----------------------------------
        folder.delete_polygon('polygon_2')
        self.assertEqual(['polygon_1', 'polygon_3'], folder.get_polygon_list())

    def test_error_move_polygon(self):
        folder = PolygonFolder('test_folder')

        with self.assertRaises(KeyError):
            folder.move_polygon('non_existent_id', 5)

    def test_move_polygon(self):
        folder = PolygonFolder('test_folder')

        folder.add_polygon('polygon_1')
        folder.add_polygon('polygon_2')
        folder.add_polygon('polygon_3')
        folder.add_polygon('polygon_4')
        folder.add_polygon('polygon_5')
        folder.add_polygon('polygon_6')
        self.assertEqual(['polygon_1', 'polygon_2', 'polygon_3', 'polygon_4', 'polygon_5', 'polygon_6'],
                         folder.get_polygon_list())

        # Test normal polygon movement in the list of polygons
        # ----------------------------------------------------
        folder.move_polygon('polygon_2', 3)
        self.assertEqual(['polygon_1', 'polygon_3', 'polygon_4', 'polygon_5', 'polygon_2', 'polygon_6'],
                         folder.get_polygon_list())

        folder.move_polygon('polygon_5', -1)
        self.assertEqual(['polygon_1', 'polygon_3', 'polygon_5', 'polygon_4', 'polygon_2', 'polygon_6'],
                         folder.get_polygon_list())

        # Test moving the polygon more than the array length
        # --------------------------------------------------
        folder.move_polygon('polygon_1', 100)
        self.assertEqual(['polygon_3', 'polygon_5', 'polygon_4', 'polygon_2', 'polygon_6', 'polygon_1'],
                         folder.get_polygon_list())

        folder.move_polygon('polygon_6', -100)
        self.assertEqual(['polygon_6', 'polygon_3', 'polygon_5', 'polygon_4', 'polygon_2', 'polygon_1'],
                         folder.get_polygon_list())


if __name__ == '__main__':
    unittest.main()
