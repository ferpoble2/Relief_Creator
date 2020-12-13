"""
Main file of the relief application.

Starts the main program, calling the engine and the logic.
"""

from src.engine.engine import Engine
from src.program.program import Program

if __name__ == '__main__':
    engine = Engine()
    program = Program(engine)
    program.initialize(program)
    program.run()
