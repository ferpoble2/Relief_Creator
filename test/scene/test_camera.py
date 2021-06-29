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


if __name__ == '__main__':
    unittest.main()
