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
from src.engine.scene.camera import Camera
from math import pi
import numpy as np


class TestCamera(unittest.TestCase):

    def test_camera_radius(self):
        camera = Camera()
        self.assertEqual(500, camera.get_radius())

        camera.modify_radius(-250)
        self.assertEqual(250, camera.get_radius())

        camera.modify_radius(1000)
        self.assertEqual(1250, camera.get_radius())

        camera.modify_radius(-2000)
        self.assertEqual(1250, camera.get_radius())

    def test_camera_azimuthal_degrees(self):
        camera = Camera()
        self.assertEqual(270, camera.get_azimuthal_grades())

        camera.modify_azimuthal_angle(pi / 2)
        self.assertEqual(0, camera.get_azimuthal_grades())

        camera.modify_azimuthal_angle(-pi / 2)
        self.assertEqual(270, camera.get_azimuthal_grades())

    def test_camera_elevation_degrees(self):
        camera = Camera()
        self.assertAlmostEqual(5.729577951308232, camera.get_elevation_grades())

        camera.modify_elevation(pi / 4)
        self.assertAlmostEqual(50.72957795130824, camera.get_elevation_grades())

        camera.modify_elevation(-pi / 8)
        self.assertAlmostEqual(28.229577951308233, camera.get_elevation_grades())

        camera.modify_elevation(-pi / 2)
        self.assertAlmostEqual(28.229577951308233, camera.get_elevation_grades())

    def test_camera_offset(self):
        camera = Camera()
        offset = camera.get_camera_offset_position()
        self.assertEqual((0, 0, 0), (offset[0], offset[1], offset[2]))

        camera.modify_camera_offset((10, -10, 50))
        offset = camera.get_camera_offset_position()
        self.assertEqual((10, -10, 50), (offset[0], offset[1], offset[2]))

        camera.modify_camera_offset((-20, 1000, -100))
        offset = camera.get_camera_offset_position()
        self.assertEqual((-10, 990, -50), (offset[0], offset[1], offset[2]))

    def test_camera_reset_values(self):
        camera = Camera()
        offset = camera.get_camera_offset_position()
        self.assertEqual((0, 0, 0), (offset[0], offset[1], offset[2]))
        self.assertAlmostEqual(5.729577951308232, camera.get_elevation_grades())
        self.assertEqual(500, camera.get_radius())

        camera.modify_camera_offset((10, -10, 50))
        camera.modify_elevation(pi / 4)
        camera.modify_azimuthal_angle(pi / 2)

        offset = camera.get_camera_offset_position()
        self.assertEqual(0, camera.get_azimuthal_grades())
        self.assertAlmostEqual(50.72957795130824, camera.get_elevation_grades())
        self.assertEqual((10, -10, 50), (offset[0], offset[1], offset[2]))

        camera.reset_values()

        offset = camera.get_camera_offset_position()
        self.assertEqual((0, 0, 0), (offset[0], offset[1], offset[2]))
        self.assertAlmostEqual(5.729577951308232, camera.get_elevation_grades())
        self.assertEqual(500, camera.get_radius())

    def test_camera_view_matrix(self):
        camera = Camera()
        view_matrix = camera.get_view_matrix()
        self.assertEqual((4, 4), view_matrix.shape)

        expected_matrix = np.load('resources/test_resources/expected_data/npy_data/test_camera_view_matrix_1.npy')
        equal_array = expected_matrix == view_matrix
        self.assertTrue(equal_array.all())

        camera.modify_camera_offset((10, -10, 50))
        camera.modify_elevation(pi / 4)
        camera.modify_azimuthal_angle(pi / 2)

        view_matrix = camera.get_view_matrix()
        self.assertEqual((4, 4), view_matrix.shape)

        expected_matrix = np.load('resources/test_resources/expected_data/npy_data/test_camera_view_matrix_2.npy')
        equal_array = expected_matrix == view_matrix
        self.assertTrue(equal_array.all())


if __name__ == '__main__':
    unittest.main()
