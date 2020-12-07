# Relief Creator

TODO: Write a better description.

# Context of the application

This project is development as a thesis project for the Computer Science department of the University of Chile and
consist on a program that is able to modify the height of geographical data using interactive controls to draw polygons
in the screen.

It is developed with the goal of making easier to modify the height of maps, without the necessity of using software or
tools not developed for that purpose.

# Instructions

To install the dependencies of the program run the following command in the root folder of the project:

    pip install -r requeriments.txt


To execute the program run the following command in the same folder:

    python ./src/main.py

It is recommended to use a virtual environment to install the dependencies: https://docs.python.org/3/tutorial/venv.html

# Code Guidelines

- Identation must be of four spaces.
- Docstring must follow the google docstring format.
- Lines must be shorter or equal than 100 characters when possible.
- All files, clases, methods and functions must be documented.
- When possible, files should contain a small program inside the block `if __name__ == __main__` with an example of the methods and definition in the file.
- Method and function definitions must have the type of the parameters and the output using `typing` from python.