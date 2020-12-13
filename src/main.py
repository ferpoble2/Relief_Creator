"""
Main file of the relief application.

Starts the main program, calling the engine and the logic. Also defines
the Program class, the main class of the program that runs everything.
"""

from src.engine.engine import Engine

if __name__ == '__main__':
    engine = Engine()
    engine.initialize(engine)
    engine.run()
