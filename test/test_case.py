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
Module that defines specific TestCases.
"""
import unittest

from src.program.program import Program


class ProgramTestCase(unittest.TestCase):
    """
    Test case for testing the application.

    Initialize the program and the engine at the beginning of each test, storing them in class variables and close the
    program at the end of the test.
    """

    def setUp(self) -> None:
        """
        Initialize the program and the engine.

        Returns: None
        """
        self.program = Program()
        self.engine = self.program.engine
        self.engine.should_use_threads(False)

    def tearDown(self) -> None:
        """
        Close the program.

        Returns: None
        """
        self.program.close()
