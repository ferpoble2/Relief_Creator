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
