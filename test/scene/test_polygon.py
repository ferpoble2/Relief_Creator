"""
File with tests related to the polygon class.
"""

import unittest
import warnings
import os

from src.engine.engine import Engine
from src.program.program import Program


class TestAddPoints(unittest.TestCase):

    def test_add_points_normal(self):
        warnings.simplefilter("ignore", ResourceWarning)

        # create program
        self.engine = Engine()
        self.program = Program(self.engine)

        # initialize variables
        self.engine.should_use_threads(False)
        self.engine.refresh_with_model_2d('resources/test_resources/cpt/cpt_1.cpt',
                                          'resources/test_resources/netcdf/test_model_2.nc')

        pol_1 = self.engine.create_new_polygon()
        self.engine.set_active_polygon(pol_1)

        self.assertEqual(self.engine.get_points_from_polygon(pol_1),
                         [])

        self.engine.add_new_vertex_to_active_polygon_using_window_coords(0, 0)
        self.assertEqual(self.engine.get_points_from_polygon(pol_1),
                         [-1.3703703703703702, 2.074074074074074, 0.5])

        self.engine.add_new_vertex_to_active_polygon_using_window_coords(0, 1)
        self.assertEqual(self.engine.get_points_from_polygon(pol_1),
                         [-1.3703703703703702, 2.074074074074074, 0.5,
                          -1.3703703703703702, 2.071111111111111, 0.5])

        self.engine.add_new_vertex_to_active_polygon_using_window_coords(0, 2)
        self.assertEqual(self.engine.get_points_from_polygon(pol_1),
                         [-1.3703703703703702, 2.074074074074074, 0.5,
                          -1.3703703703703702, 2.071111111111111, 0.5,
                          -1.3703703703703702, 2.0681481481481483, 0.5])

        self.engine.add_new_vertex_to_active_polygon_using_window_coords(0, 3)
        self.assertEqual(self.engine.get_points_from_polygon(pol_1),
                         [-1.3703703703703702, 2.074074074074074, 0.5,
                          -1.3703703703703702, 2.071111111111111, 0.5,
                          -1.3703703703703702, 2.0681481481481483, 0.5,
                          -1.3703703703703702, 2.065185185185185, 0.5])

    def test_repeated_point(self):
        warnings.simplefilter("ignore", ResourceWarning)

        # create program
        self.engine = Engine()
        self.program = Program(self.engine)

        # intialize variables
        self.engine.should_use_threads(False)
        self.engine.refresh_with_model_2d('resources/test_resources/cpt/cpt_1.cpt',
                                          'resources/test_resources/netcdf/test_model_2.nc')

        pol = self.engine.create_new_polygon()
        self.engine.set_active_polygon(pol)
        self.engine.add_new_vertex_to_active_polygon_using_window_coords(0, 0)
        self.engine.add_new_vertex_to_active_polygon_using_window_coords(0, 0)
        self.engine.add_new_vertex_to_active_polygon_using_window_coords(0, 0)
        self.engine.add_new_vertex_to_active_polygon_using_window_coords(0, 0)

        self.assertEqual(self.engine.get_points_from_polygon(pol),
                         [-1.3703703703703702, 2.074074074074074, 0.5])

    def test_line_intersection(self):
        warnings.simplefilter("ignore", ResourceWarning)

        # create program
        self.engine = Engine()
        self.program = Program(self.engine)

        # intialize variables
        self.engine.should_use_threads(False)
        self.engine.refresh_with_model_2d('resources/test_resources/cpt/cpt_1.cpt',
                                          'resources/test_resources/netcdf/test_model_2.nc')

        pol = self.engine.create_new_polygon()
        self.engine.set_active_polygon(pol)
        self.engine.add_new_vertex_to_active_polygon_using_window_coords(0, 0)
        self.engine.add_new_vertex_to_active_polygon_using_window_coords(1, 0)
        self.engine.add_new_vertex_to_active_polygon_using_window_coords(0.5, 0.5)
        self.engine.add_new_vertex_to_active_polygon_using_window_coords(0.5, -0.5)

        self.assertEqual(self.engine.get_points_from_polygon(pol),
                         [-1.3703703703703702, 2.074074074074074, 0.5,
                          -1.3674074074074074, 2.074074074074074, 0.5,
                          -1.3688888888888888, 2.0725925925925925, 0.5])


class TestPlanarity(unittest.TestCase):

    def test_planarity_polygon(self):
        warnings.simplefilter("ignore", ResourceWarning)

        # create program
        self.engine = Engine()
        self.program = Program(self.engine)

        # intialize variables
        self.engine.should_use_threads(False)
        self.engine.refresh_with_model_2d('resources/test_resources/cpt/cpt_1.cpt',
                                          'resources/test_resources/netcdf/test_model_2.nc')

        pol_planar = self.engine.create_new_polygon()
        self.engine.set_active_polygon(pol_planar)
        self.engine.add_new_vertex_to_active_polygon_using_window_coords(0, 0)
        self.engine.add_new_vertex_to_active_polygon_using_window_coords(1, 0)
        self.engine.add_new_vertex_to_active_polygon_using_window_coords(2, 0)
        self.engine.add_new_vertex_to_active_polygon_using_window_coords(2, 1)
        self.engine.add_new_vertex_to_active_polygon_using_window_coords(1, 1)
        self.engine.add_new_vertex_to_active_polygon_using_window_coords(0, 1)
        self.assertTrue(self.engine.is_polygon_planar(pol_planar))

        pol_not_planar = self.engine.create_new_polygon()
        self.engine.set_active_polygon(pol_not_planar)
        self.engine.add_new_vertex_to_active_polygon_using_window_coords(0, 0)
        self.engine.add_new_vertex_to_active_polygon_using_window_coords(1, 0)
        self.engine.add_new_vertex_to_active_polygon_using_window_coords(1, -1)
        self.engine.add_new_vertex_to_active_polygon_using_window_coords(2, -0.5)
        self.assertFalse(self.engine.is_polygon_planar(pol_not_planar))


if __name__ == '__main__':
    unittest.main()
