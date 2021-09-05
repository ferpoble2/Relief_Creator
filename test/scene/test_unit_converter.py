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
File with tests related to the conversion of units used in the scene to transform coordinates of the model.
"""
import unittest

from src.engine.scene.unit_converter import UnitConverter


class TestConversionValues(unittest.TestCase):

    def test_kilometers_meters(self):
        self.assertEqual(0.001, UnitConverter().meter_to_kilometer(),
                         'Factor to convert meters to kilometers is incorrect.')
        self.assertEqual(1000, UnitConverter().kilometer_to_meter(),
                         'Factor to convert kilometers to meters is incorrect.')

    def test_meter_to_degrees(self):
        self.assertEqual(0.0001 / 111, UnitConverter().meter_to_degrees(),
                         'Factor to convert meters to degrees is incorrect.')


if __name__ == '__main__':
    unittest.main()
