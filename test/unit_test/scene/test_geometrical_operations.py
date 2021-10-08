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
Module in charge of the testing of the module geometrical operations.
"""

import unittest

import numpy as np

from src.engine.scene.geometrical_operations import get_max_min_inside_polygon, merge_matrices


class TestMinMaxPolygon(unittest.TestCase):

    def test_min_max_normal(self):

        # create and set the points on the grid
        points = np.zeros((10, 10, 3))
        for row in range(10):
            for col in range(10):
                points[row, col, 0] = col
                points[row, col, 1] = row

        # create the polygon
        polygon_points = [0.9, 0, 0,
                          5, 0, 0,
                          1, 5, 0]

        # create heights of the map
        height = np.zeros((10, 10))
        height[1, 1] = -15
        height[2, 2] = 30

        self.assertEqual((30, -15), get_max_min_inside_polygon(points,
                                                               polygon_points,
                                                               height),
                         'Minimum and maximum values are not the one inside the polygon.')

    def test_min_max_same_value(self):

        # create and set the points on the grid
        points = np.zeros((10, 10, 3))
        for row in range(10):
            for col in range(10):
                points[row, col, 0] = col
                points[row, col, 1] = row

        # create the polygon
        polygon_points = [1, 0, 0,
                          5, 0, 0,
                          1, 5, 0]

        # create heights of the map
        height = np.ones((10, 10))
        height = height * 150

        self.assertEqual((150, 150), get_max_min_inside_polygon(points,
                                                                polygon_points,
                                                                height),
                         'Minimum and maximum values are not the one inside the polygon.')

    def test_min_max_polygon_outside(self):

        # create and set the points on the grid
        points = np.zeros((10, 10, 3))
        for row in range(10):
            for col in range(10):
                points[row, col, 0] = col
                points[row, col, 1] = row

        # create the polygon
        polygon_points = [100, 0, 0,
                          150, 0, 0,
                          125, 50, 0]

        # create heights of the map
        height = np.ones((10, 10))
        height = height * 150

        (max_, min_) = get_max_min_inside_polygon(points,
                                                  polygon_points,
                                                  height)
        self.assertEqual((np.nan, np.nan), (max_, min_),
                         'Minimum and maximum values are not the one inside the polygon.')


class TestMergeMatrices(unittest.TestCase):

    def test_merge_normal_matrices(self):
        first_matrix = np.array([[1, 2, 3],
                                 [4, np.nan, 6],
                                 [7, 8, 9]])
        second_matrix = np.array([[np.nan, np.nan, np.nan],
                                  [np.nan, 5, np.nan],
                                  [np.nan, np.nan, np.nan]])

        np.testing.assert_array_equal(np.array([[1, 2, 3],
                                                [4, 5, 6],
                                                [7, 8, 9]]),
                                      merge_matrices(first_matrix,
                                                     second_matrix))

    def test_do_not_modify_matrices(self):
        first_matrix = np.array([[1, 2, 3],
                                 [4, np.nan, 6],
                                 [7, 8, 9]])
        second_matrix = np.array([[np.nan, np.nan, np.nan],
                                  [np.nan, 5, np.nan],
                                  [np.nan, np.nan, np.nan]])

        merge_matrices(first_matrix, second_matrix)

        np.testing.assert_array_equal(np.array([[1, 2, 3],
                                                [4, np.nan, 6],
                                                [7, 8, 9]]),
                                      first_matrix,
                                      "Base matrix was modified on the process.")

        np.testing.assert_array_equal(np.array([[np.nan, np.nan, np.nan],
                                                [np.nan, 5, np.nan],
                                                [np.nan, np.nan, np.nan]]),
                                      second_matrix,
                                      "Second matrix was modified on the process.")

    def test_merge_shared_nan_values(self):
        first_matrix = np.array([[1, 2, 3],
                                 [4, np.nan, np.nan],
                                 [np.nan, np.nan, np.nan]])
        second_matrix = np.array([[np.nan, np.nan, np.nan],
                                  [np.nan, 5, np.nan],
                                  [np.nan, np.nan, 15]])

        np.testing.assert_array_equal(np.array([[1, 2, 3],
                                                [4, 5, np.nan],
                                                [np.nan, np.nan, 15]]),
                                      merge_matrices(first_matrix,
                                                     second_matrix),
                                      "Matrix generated is not equal to the expected.")

    def test_merge_shared_numeric_values(self):
        first_matrix = np.array([[1, 2, 3],
                                 [4, np.nan, np.nan],
                                 [np.nan, np.nan, np.nan]])
        second_matrix = np.array([[20, 15, 30],
                                  [np.nan, 5, 6],
                                  [7, 8, 9]])

        np.testing.assert_array_equal(np.array([[1, 2, 3],
                                                [4, 5, 6],
                                                [7, 8, 9]]),
                                      merge_matrices(first_matrix,
                                                     second_matrix),
                                      "Matrix generated is not equal to the expected.")


if __name__ == '__main__':
    unittest.main()
