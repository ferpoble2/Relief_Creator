# Source directory

In this directory is located all the code that runs the program.

## Errors

The folder `error` contain manually created exceptions used in the program.

## Fonts and Icons

The fonts used in the engine are in the directory `engine/GUI/fonts/`, and are used by the engine to render the User interface. To change the font used in the different windows of the GUI it is necessary to call the correct methods on the `GUIManager` class.

- The Icons are stored in the directory `engine/GUI/icons/`, and are used by the engine to draw imagen on the GUI. 
    - The images are loaded, stored and used as OpenGl textures on the engine.
    - The icons must be images in format `.png` and must be added to the method `__load_icons` of the class `GUIManager` to be able to use them.
    - The use of icons is limited only to the windows of the GUI.

## Type Hinting

The source code of the program uses type hinting on the definition of the methods and functions. Due to python 3.8, these classes should be imported to make use of them, if not, then the linting will show an error.

This module do a fake import of the classes used in the type hinting of the method and function defined on the code of the program, solving the linting errors.

## Source Code
- The `main.py` file contains the main function that executes the program.

- The `utils.py` file contains different functionality used by the program but that doesn't belong to any package.

- All the other folders are modules that the program uses to work.
