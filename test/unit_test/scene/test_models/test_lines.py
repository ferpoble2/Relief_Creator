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
Module with tests related to the Lines model of the program.

Since it is necessary a Scene for the creation of the models, the tests need to create a full program to run.
"""

import unittest

import numpy as np

from src.engine.scene.model.lines import Lines
from test.test_case import ProgramTestCase


class TestCreateLines(ProgramTestCase):

    def test_creation_with_points(self):
        points_lines_model = [[-5, 10, 0.5],
                              [-5, 0, 0.5],
                              [5, 10, 0.5],
                              [5, 0, 0.5]]
        lines_model = Lines(self.engine.scene, np.array(points_lines_model))

        np.testing.assert_array_equal([-5, 10, 0.5, -5, 0, 0.5,
                                       -5, 0, 0.5, 5, 10, 0.5,
                                       5, 10, 0.5, 5, 0, 0.5], lines_model.get_vertices_array(),
                                      'Vertices are not the expected.')
        np.testing.assert_array_equal([0, 1, 2, 3, 4, 5], lines_model.get_indices_array(),
                                      'Indices are not equal to the expected.')


class TestLinesRemoveLines(ProgramTestCase):

    def test_remove_with_initial_lines(self):
        initial_points = [[-5, 10, 0.5],
                          [-5, 0, 0.5],
                          [5, 10, 0.5],
                          [5, 0, 0.5]]

        lines_model = Lines(self.engine.scene, np.array(initial_points))
        lines_model.remove_last_added_line()

        np.testing.assert_array_equal([-5, 10, 0.5, -5, 0, 0.5,
                                       -5, 0, 0.5, 5, 10, 0.5], lines_model.get_vertices_array(),
                                      'Vertices are not the expected.')
        np.testing.assert_array_equal([0, 1, 2, 3], lines_model.get_indices_array(),
                                      'Indices are not equal to the expected.')

    def test_remove_lines(self):
        lines_model = Lines(self.engine.scene)
        lines_model.add_line((-5, 10, 0.5),
                             (-5, 0, 0.5), )
        lines_model.add_line((-5, 0, 0.5),
                             (5, 10, 0.5))
        lines_model.add_line((5, 10, 0.5),
                             (5, 0, 0.5))
        lines_model.remove_last_added_line()

        np.testing.assert_array_equal([-5, 10, 0.5, -5, 0, 0.5,
                                       -5, 0, 0.5, 5, 10, 0.5], lines_model.get_vertices_array(),
                                      'Vertices are not the expected.')
        np.testing.assert_array_equal([0, 1, 2, 3], lines_model.get_indices_array(),
                                      'Indices are not equal to the expected.')


class TestLinesAddNewLines(ProgramTestCase):

    def test_add_points_lines(self):
        lines_model = Lines(self.engine.scene)
        lines_model.add_line((-5, 10, 0.5),
                             (-5, 0, 0.5), )
        lines_model.add_line((-5, 0, 0.5),
                             (5, 10, 0.5))
        lines_model.add_line((5, 10, 0.5),
                             (5, 0, 0.5))

        np.testing.assert_array_equal([-5, 10, 0.5, -5, 0, 0.5,
                                       -5, 0, 0.5, 5, 10, 0.5,
                                       5, 10, 0.5, 5, 0, 0.5], lines_model.get_vertices_array(),
                                      'Vertices are not the expected.')
        np.testing.assert_array_equal([0, 1, 2, 3, 4, 5], lines_model.get_indices_array(),
                                      'Indices are not equal to the expected.')

    def test_add_lines_with_initial_lines(self):
        initial_points = [[-5, 10, 0.5],
                          [-5, 0, 0.5],
                          [5, 10, 0.5]]

        lines_model = Lines(self.engine.scene, np.array(initial_points))
        lines_model.add_line((5, 10, 0.5),
                             (5, 0, 0.5))

        np.testing.assert_array_equal([-5, 10, 0.5, -5, 0, 0.5,
                                       -5, 0, 0.5, 5, 10, 0.5,
                                       5, 10, 0.5, 5, 0, 0.5], lines_model.get_vertices_array(),
                                      'Vertices are not the expected.')
        np.testing.assert_array_equal([0, 1, 2, 3, 4, 5], lines_model.get_indices_array(),
                                      'Indices are not equal to the expected.')


if __name__ == '__main__':
    unittest.main()
