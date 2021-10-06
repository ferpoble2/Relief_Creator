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
File with the tests related to the functionality that imports CPT files into the program.
"""
import json
import unittest
import warnings

from src.input.CTP import read_file


class TestReadCPTFile(unittest.TestCase):

    def setUp(self) -> None:
        """Logic executed before every test."""
        warnings.simplefilter("ignore", ResourceWarning)

    def test_reading_normal_files(self):
        with open('resources/test_resources/expected_data/json_data/test_data_CPT_1.json') as f:
            data_1 = json.load(f)
            data_read = read_file('resources/test_resources/cpt/cpt_1.cpt')
            self.assertEqual(data_1, data_read, 'Data read from CPT file is not what is expected.')

        with open('resources/test_resources/expected_data/json_data/test_data_CPT_2.json') as f:
            data_2 = json.load(f)
            data_read = read_file('resources/test_resources/cpt/cpt_2.cpt')
            self.assertEqual(data_2, data_read, 'Data read from CPT file is not what is expected.')


if __name__ == '__main__':
    unittest.main()
