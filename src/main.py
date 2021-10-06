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
from src.program.parser import get_command_line_arguments
from src.program.program import Program

if __name__ == '__main__':
    # Get the arguments to use for the program.
    command_line_args = get_command_line_arguments()
    debug_mode = command_line_args.debug if 'debug' in command_line_args else False

    # Create the program
    program = Program(debug_mode=debug_mode)

    # Start the program
    program.process_arguments(command_line_args)
    program.run()
