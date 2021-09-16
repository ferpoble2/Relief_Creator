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
import warnings

from src.program.program import Program


class TestAddPoints(unittest.TestCase):

    def setUp(self) -> None:
        """
        Method that executes before every test.
        """
        warnings.simplefilter("ignore", ResourceWarning)

        # create program
        self.program = Program()
        self.engine = self.program.engine

        # initialize variables
        self.engine.should_use_threads(False)
        self.engine.load_netcdf_file('resources/test_resources/cpt/cpt_1.cpt',
                                     'resources/test_resources/netcdf/test_model_2.nc')

    def tearDown(self) -> None:
        """
        Delete all temporary files created by the program on the setup or testing processes.

        Returns: None
        """
        self.program.close()

    def test_add_points_normal(self):
        warnings.simplefilter("ignore", ResourceWarning)

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
        warnings.simplefilter("ignore", ResourceWarning)

        pol = self.engine.create_new_polygon()
        self.engine.set_active_polygon(pol)
        self.engine.add_new_vertex_to_active_polygon_using_real_coords(0, 0)
        self.engine.add_new_vertex_to_active_polygon_using_real_coords(0, 0)
        self.engine.add_new_vertex_to_active_polygon_using_real_coords(0, 0)
        self.engine.add_new_vertex_to_active_polygon_using_real_coords(0, 0)

        self.assertEqual(self.engine.get_points_from_polygon(pol),
                         [0, 0, 0.5])

    def test_line_intersection(self):
        warnings.simplefilter("ignore", ResourceWarning)

        pol = self.engine.create_new_polygon()
        self.engine.set_active_polygon(pol)
        self.engine.add_new_vertex_to_active_polygon_using_real_coords(0, 0)
        self.engine.add_new_vertex_to_active_polygon_using_real_coords(1, 0)
        self.engine.add_new_vertex_to_active_polygon_using_real_coords(0.5, 0.5)
        self.engine.add_new_vertex_to_active_polygon_using_real_coords(0.5, -0.5)

        self.assertEqual([0, 0, 0.5, 1, 0, 0.5, 0.5, 0.5, 0.5],
                         self.engine.get_points_from_polygon(pol))


class TestPlanarity(unittest.TestCase):

    def test_planarity_polygon(self):
        warnings.simplefilter("ignore", ResourceWarning)

        # create program
        self.program = Program()
        self.engine = self.program.engine

        # initialize variables
        self.engine.should_use_threads(False)
        self.engine.load_netcdf_file('resources/test_resources/cpt/cpt_1.cpt',
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

        self.program.close()


class TestUndoAction(unittest.TestCase):

    def test_undo_point_added(self):
        warnings.simplefilter("ignore", ResourceWarning)

        program = Program()
        engine = program.engine

        engine.should_use_threads(False)
        engine.load_netcdf_file(
            'resources/test_resources/cpt/colors_0_100_200.cpt',
            'resources/test_resources/netcdf/test_file_1.nc'
        )

        pol_id = engine.create_new_polygon()

        engine.set_active_polygon(pol_id)
        engine.add_new_vertex_to_active_polygon_using_real_coords(50, 50)
        engine.add_new_vertex_to_active_polygon_using_real_coords(60, 60)

        self.assertEqual([50, 50, 0.5, 60, 60, 0.5],
                         engine.get_points_from_polygon(pol_id),
                         'Polygon does not store points coordinates correctly.')

        program.set_active_tool('create_polygon')
        engine.undo_action()
        self.assertEqual([50, 50, 0.5],
                         engine.get_points_from_polygon(pol_id),
                         'Last point of the polygon was not removed correctly.')

        program.close()


if __name__ == '__main__':
    unittest.main()
