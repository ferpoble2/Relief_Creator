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
File with tests related to the polygon class.
"""
import unittest

from src.program.tools import Tools
from test.test_case import ProgramTestCase


class TestAddPoints(ProgramTestCase):

    def setUp(self) -> None:
        """
        Method that executes before every test.
        """
        super().setUp()
        self.engine.create_model_from_file('resources/test_resources/cpt/cpt_1.cpt',
                                           'resources/test_resources/netcdf/test_model_2.nc')

    def test_add_points_normal(self):
        pol_1 = self.engine.create_new_polygon()
        self.engine.set_active_polygon(pol_1)

        self.assertEqual(self.engine.get_points_from_polygon(pol_1),
                         [])

        self.engine.add_new_vertex_to_active_polygon_using_real_coords(0, 0)
        self.assertEqual(self.engine.get_points_from_polygon(pol_1),
                         [0, 0, 0.5])

        self.engine.add_new_vertex_to_active_polygon_using_real_coords(0, 1)
        self.assertEqual(self.engine.get_points_from_polygon(pol_1),
                         [0, 0, 0.5,
                          0, 1, 0.5])

        self.engine.add_new_vertex_to_active_polygon_using_real_coords(0, 2)
        self.assertEqual(self.engine.get_points_from_polygon(pol_1),
                         [0, 0, 0.5,
                          0, 1, 0.5,
                          0, 2, 0.5])

        self.engine.add_new_vertex_to_active_polygon_using_real_coords(0, 3)
        self.assertEqual(self.engine.get_points_from_polygon(pol_1),
                         [0, 0, 0.5,
                          0, 1, 0.5,
                          0, 2, 0.5,
                          0, 3, 0.5])

    def test_repeated_point(self):
        pol = self.engine.create_new_polygon()
        self.engine.set_active_polygon(pol)
        self.engine.add_new_vertex_to_active_polygon_using_real_coords(0, 0)
        self.engine.add_new_vertex_to_active_polygon_using_real_coords(0, 0)
        self.engine.add_new_vertex_to_active_polygon_using_real_coords(0, 0)
        self.engine.add_new_vertex_to_active_polygon_using_real_coords(0, 0)

        self.assertEqual(self.engine.get_points_from_polygon(pol),
                         [0, 0, 0.5])

    def test_line_intersection(self):
        pol = self.engine.create_new_polygon()
        self.engine.set_active_polygon(pol)
        self.engine.add_new_vertex_to_active_polygon_using_real_coords(0, 0)
        self.engine.add_new_vertex_to_active_polygon_using_real_coords(1, 0)
        self.engine.add_new_vertex_to_active_polygon_using_real_coords(0.5, 0.5)
        self.engine.add_new_vertex_to_active_polygon_using_real_coords(0.5, -0.5)

        self.assertEqual([0, 0, 0.5, 1, 0, 0.5, 0.5, 0.5, 0.5],
                         self.engine.get_points_from_polygon(pol))


class TestPlanarity(ProgramTestCase):

    def test_planarity_polygon(self):
        self.engine.create_model_from_file('resources/test_resources/cpt/cpt_1.cpt',
                                           'resources/test_resources/netcdf/test_model_2.nc')

        pol_planar = self.engine.create_new_polygon()
        self.engine.set_active_polygon(pol_planar)
        self.engine.add_new_vertex_to_active_polygon_using_real_coords(0, 0)
        self.engine.add_new_vertex_to_active_polygon_using_real_coords(1, 0)
        self.engine.add_new_vertex_to_active_polygon_using_real_coords(2, 0)
        self.engine.add_new_vertex_to_active_polygon_using_real_coords(2, 1)
        self.engine.add_new_vertex_to_active_polygon_using_real_coords(1, 1)
        self.engine.add_new_vertex_to_active_polygon_using_real_coords(0, 1)
        self.assertTrue(self.engine.is_polygon_planar(pol_planar))

        pol_not_planar = self.engine.create_new_polygon()
        self.engine.set_active_polygon(pol_not_planar)
        self.engine.add_new_vertex_to_active_polygon_using_real_coords(0, 0)
        self.engine.add_new_vertex_to_active_polygon_using_real_coords(1, 0)
        self.engine.add_new_vertex_to_active_polygon_using_real_coords(1, -1)
        self.engine.add_new_vertex_to_active_polygon_using_real_coords(2, -0.5)
        self.assertFalse(self.engine.is_polygon_planar(pol_not_planar))


class TestUndoAction(ProgramTestCase):

    def test_undo_point_added(self):
        self.engine.create_model_from_file(
            'resources/test_resources/cpt/colors_0_100_200.cpt',
            'resources/test_resources/netcdf/test_file_1.nc'
        )

        pol_id = self.engine.create_new_polygon()

        self.engine.set_active_polygon(pol_id)
        self.engine.add_new_vertex_to_active_polygon_using_real_coords(50, 50)
        self.engine.add_new_vertex_to_active_polygon_using_real_coords(60, 60)

        self.assertEqual([50, 50, 0.5, 60, 60, 0.5],
                         self.engine.get_points_from_polygon(pol_id),
                         'Polygon does not store points coordinates correctly.')

        self.program.set_active_tool(Tools.create_polygon)
        self.engine.undo_action()
        self.assertEqual([50, 50, 0.5],
                         self.engine.get_points_from_polygon(pol_id),
                         'Last point of the polygon was not removed correctly.')


if __name__ == '__main__':
    unittest.main()
