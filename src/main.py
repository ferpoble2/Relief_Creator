# BEGIN GPL LICENSE BLOCK
#
#     This program is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# END GPL LICENSE BLOCK

"""
Main file of the relief application.

Starts the main program, calling the engine and the logic.
"""
from src.engine.engine import Engine
from src.program.program import Program
from src.program.parser import get_command_line_arguments

if __name__ == '__main__':
    engine = Engine()
    program = Program(engine)

    program.process_arguments(get_command_line_arguments())
    program.run()
