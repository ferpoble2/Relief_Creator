# Relief Creator

Simple application to modify terrain using polygons and functions over the points of the terrain.

# Context of the application

This project is development as a thesis project for the Computer Science department of the University of Chile and
consist on a program that is able to modify the height of geographical data using interactive controls to draw polygons
in the screen.

It is developed with the goal of making easier to modify the height of maps, without the necessity of using software or
tools not developed for that purpose.

# Usage

## How to use the program

### Shortcuts

This is a list of shortcuts implemented in the program to make the usage of it more fast.

- CTRL + O: Load a netcdf file on the program.
- CTRL + T: Loaf a ctp file on the program.
- CTRL + Z: Undo the last action (Not in all tools).
- CTRL + L: Load a shapefile file into the program.


In 2D mode:
- WASD: Movement of the loaded map
- R: Reload the map with the current resolution
- M: Change to `Move Map` tool.
- Scroll: Zoom In/Out

In 3D mode:
- W/S: Change elevation.
- A/D: Change azimuthal angle.
- Scroll: Get closer/farther.
- UP/DOWN: Move the camera in the y-axis.
- LEFT/RIGHT: Move the camera in the x-axis.

NOTE: shortcuts does not work when there is a popup in the program.

# Instructions for developers

To install the dependencies of the program run the following command in the root folder of the project:

    pip install -r requeriments.txt

To execute the program, first you need to add the root directory to the PYTHONPATH variable, in windows, in a console CMD run the following command in the root directory of the project:

	set PYTHONPATH=.

In a system with Linux distribution run the following command:

	export PYTHONPATH=.

If you use a mac, run the following command:

	export PYTHONPATH="."

Then, to execute the program run the following command:

    python src/main.py

It is recommended to use a virtual environment to install the dependencies: https://docs.python.org/3/tutorial/venv.html

(If you use windows and use a virtual environment called *venv* then running the command `make run-windows` will run the project)

# How to build

The application can be built using the command `auto-py-to-exe` (or the equivalent `make build-executable`) and then importing the file `build_conf.json` that is on the root of the project. Make sure to create a virtual environment with python and install all the dependencies from the file `requeriments.txt` before launching the program.

The command opens a window application where one can configure how to create a .exe program from python, under the
settings tab one can import a configuration file, there is where the file `build_conf.json` must be imported.

After that just press the button at the end of the GUI application to generate the program.

The program is in the `output` folder under the name of ReliefeCreator.

IMPORTANT: In the section of additional files, the folders to include must have the full path writen. Due to this, the paths that are written by default must be changed before generating the .exe to the path where the project is in the computer.

# How to run tests

The project include inside the folder `test` different types of tests that check the functionality of the program. These tests were written using the unit tests library of the Python language.

To run the tests, add the root directory of the project to the PYTHONPATH variable and then execute the following command inside the root folder of the project:

```
python -m unittest discover .\test
```

This will run all the tests inside the folder `test`.

All the dependencies of the project must be installed for the tests to run correctly.

# Tools

There is a number of tools that form part of the engine, they are stored as strings by the program class. Here is the list of all tools of the program:

- move_map: Tool that is active when moving the 2D map on the engine.
- create_polygon: Tool to create polygons on the screen.

Only one tool can be active at a given time.

Note: The name from above is not showed in the tools frame of the program but is the one used by the program.

# How to extend the program

## How to create new frames on the application

The program uses PyIMGUI to define the GUI of the application. This is a library that allows to create easy menus, buttons and other GUI elements in applications that use OpenGL. The documentation about how to use it can be found in the following link https://pyimgui.readthedocs.io/en/latest/reference/imgui.core.html.

The GUIManager class is the one who controls all the GUI elements, this one is the responsible for the management of the different windows and frames that the application uses.

All windows showed in the application, either on the 2D mode or the 3D one, are instances of the Frame class or a class that inherit from it. All classes that inherit from the Frame class must define the render method. This method is called from the GUIManager in the context of rendering the IMGUI frames each frame, updating the GUI of the application.

To extend the functionality of the application with a new window or button, one must create or modify a class that inherit from the Frame class and define the rendering process that must be executed in every frame. The rendering must use the IMGUI functions to create windows  on the program and buttons.

The code on the render method must look something like this:

```python
def render():
    imgui.begin("name of the window")
    ...
    if imgui.button('somebutton'):
        ...
    ...
    imgui.end()
```

After creating the class and adding the logic to it, an instance of the class must be added to the lists of components on the GUIManager class. There are two lists that are defined in the constructor of the GUIManager class, one for the 2D mode and one for the 3D mode, that define the windows to show in the application, an instance of the new created class must be added to the lists to be rendered by the application.

The Frame class also define the method post-render, method that is called at the end of the rendering process. This is useful to avoid ID errors when creating popups, since they are called by name, they must be defined at the end of the rendering process after all windows where draw on the screen. The definition of this method in the classes that inherit from Frame is not obligatory.

## How to get the data of the different components of the application

The GUIManager, and all the components of the application, get the data from the Engine component. To keep the program organized, all frames must get the data that they need from the GUIManager class, and is the GUIManager the one that should ask the information to the Engine component.

The engine, as the center of the program, can get the data from all the other components by calling the methods that they have defined.

Most of the data can be obtained using the already defined methods on the engine, but if you want to update the program with new functionality, then you have to define the method to get the data in the respective component, and then have the engine call that method to get the data. This way the components remain organized will still being efficient.

To see a diagram with all the components of the program, see the diagram generated by PlantUML located at `docs/objects/main_objects.puml`.

## How to add new functionality to the program

How to add new functionality depends on the functionality to add to the program, depending on the type of functionality to add it must be added in a different component or class.

The components and the type of functionality expected in their interior are defined as follows:

+ Scene: Functionality related to the maps, 2D or 3D, and the modifications that happens with them and the polygons.
+ GUI: Functionality related to the UI of the program.
+ Render: Functionality related to the rendering process and the main cycle of the program.
+ Controller: Functionality related to the keyboard/mouse input and how the program must answer to the events.
+ Program: Functionality related to the state of the program in a given moment.
+ Engine: Functionality related to the communication of different components of the program. Functionality related to how the program must answer possible errors that happens. Functionality related to the threads and execution of tasks.
+ Output: Functionality related to the generation of output files.
+ Input: Functionality related to reading of input files.

Each component is composed from one package than can or cannot have more sub-packages in its interior.

Once located where the functionality to add should be, there are two things to consider:

1. The functionality must be called from the engine.
2. The possible errors that can happen with the functionality must be handled by the engine.

The functionality defined in the program must be called by the engine, this is to keep the code organized and object oriented, allowing to change the code inside the components while keeping the same API on the engine.

The second point is related to the first and is to keep the error handling process the more organized possible, being the engine the one in charge of handling all possible errors that happens with the program.

## Example

So, for example, if there is the need to add a new functionality to apply a filter to the full map when the  user press a button, then the following steps should be done to add that functionality to the program:

1. Locate in which component the functionality should be added (in this case, it must be added on the Scene component, in the Scene class and the TransformationHelper class).

2. Implement the functionality in the given component, either modifying and existent class or creating a new one, and add a method that allows to use the functionality to the class that is connected to the engine (in this case, add a method to execute the logic in the Scene class).

3. Implement a new method to the engine class where the new functionality is called and all the possible errors are handled.

   This should be the end of a normal process, in the current example we still need to add a button to connect the functionality implemented to the GUI.

4. Create a new class that inherit from the Frame class or modify an already existing frame and add the button.

5. Define in the GUIManager class a method that calls the method defined previously in the Engine.

6. Make the added button call the method defined in the  GUIManager to run the functionality when it is pressed.

   (The order in which the functions are called to run the logic is as follows at the end: Frame=>GUIManager=>Engine=>Scene)

In this example, we needed to modify not just the Scene and the Engine but also the GUI to trigger the functionality. This does not have to be always the case, the functionality can be triggered also by events, in which case the Controller must be modified or by an action made by another component. 

To keep things organized and OOP, all functionality of a component that call functionality located in another component must be called using the engine.

# About the controller

The program uses two types of controllers to maage the input from the user, one is the controller that the library `imgui` uses to process the inputs of the user related to the GUI, and the other is the one stored in the class `Controller`.

Both controllers are used in the program, the controller stored in the class `Controller` is the one in charge of calling the controller from `imgui`whenever is necessary.

# About the camera

For the 3D rendering, the program uses a 3D camera that uses spherical coordinates.

In this program, the coordinates used are (r,phi,theta), where the phi angle correspond to the azimuthal angle (parallel to the xy plane) and the theta angle correspond with the elevation angle.

Something to consider is that the elevation angle (theta) starts from the top, this means that the point (1,0,0) in spherical coordinates correspond to the point (0,0,1) in cartesian coordinates.

# Reading NetCDF files

The file `src/input/NetCDF.py` is the one in charge of reading the files in format NetCDF and generate numpy arrays.

To achieve this, the program reads the contents of the file using the NetCDF4 library. That generates a dictionary-like
object with the data of the file, then, the program search in the dictionary for the keys that have information about
the latitude, longitude and height.

## How to add more keys to search for in the netcdf files

If at some point, in the moment of loading a file the program hits a KeyError, then is highly probable that the netcdf
file have keys with another name that the ones the program uses.

At the beginning of the file `src/input/NetCDF.py` there are three variables, `LONGITUDE_KEYS`, `LATITUDE_KEYS` and
`HEIGHT_KEYS`.

The first is the list of keys that the program will use to get the longitude data from the netcdf files, the second is
the list of keys that the program will use to get the latitude data and the third is the list of keys that the program 
will use to get the height data.

To add a new key for the program to use to search for the data, just add a new string with the name of the key at 
the end of the list that need to be modified.

[comment]: <> "TODO: Add a secttion about how to add a new frame to the engine."

# About the logging system

The program uses the python `logging` library to generate loggers and then use them to log information about the 
program.

To keep consistency between the format used to log in the different modules of the program, in the file `src/utils.py`
is defined the function `get_logger(module='some_module')`, this function generates a `logger` with the correct format 
to use in the modules.

The rule to follow is to always get the logger from this function and to use as module the name of the file, this way
the debugging process become easier. 

The loggers generated logs to the standard output (console) but also store the logs in files in the `src/logs/` folder.
In this folder each module logs to a specific file.

In the file `src/utils.py` are defined the following variables that modify the behaviour of the loggers:

- LOG_TO_FILE: If logging or not to a file
- LOG_TO_CONSOLE: If logging or not to the console
- LOG_LEVEL: Log level to use for the logs
- LOG_FILE_LEVEL: Log level to use to logs in the files
- LOG_ONLY_LISTED_MODULES: If log only listed modules or log every module
- LOG_LIST_MODULES: List of modules to log if LOG_ONLY_LISTED_MODULES is true

# About the parallel tasks on the engine

The engine has implemented two main pipelines to delegate tasks to some time in the future, tasks and parallel tasks.

## Tasks

Tasks are code that will be executed after some number of frames have passed, this is, the code executed will be delayed
some number of frames.

The `engine`, at the beginning of each frame, checks if there is pending tasks to execute, if there is, then checks 
if the frame count of them is Zero, if it is, then the engine execute the code, if not, then the engine subtract 1 from
the frame count.

The only way to add tasks to the queue is with the method `set_task_for_next_frame` of the class `engine`.  This method 
receive the function to be executed after the next frame. The function will be called without any arguments.

## Parallel tasks

Parallel tasks are code that will be executed in parallel along with the main pipeline of the engine, this is, will be 
executed while the engine do the rendering of the application.

These tasks are executed in parallel using threads, and since threads share the memory and variables, it is recommended
to not do anything else when a thread is running something. (this can be achieved setting a load screen on the program
using the method `set_loading(True)` of the class `Program`).

To set a parallel task on the engine it is necessary to use the method `set_thread_task`, the first parameter of the 
method ( `parallel_task` ) is the function to execute in parallel and the second parameter ( `then` ) is a function that will be executed after
the thread finish its execution. This last function will be executed in the main thread.

To achieve this, when a parallel task is settled, the engine stores the thread in a internal variable, and, in each frame,
the engine ask the thread if it finished its execution, if it finished, then the engine execute the function given as
second parameter, if not, then the engine does nothing.

The parameters of the method `set_thread_task` are called `parallel_task` and `then`, they are called that way to 
emulate how threads work in the language Javascript. This implementation of parallel tasks is a bit difficult to work
with, but give a lot of benefits, first, it is possible to execute code after the threads ends, not having to implement
on every thread a mechanism to check if the thread ended, second, it is possible to set new thread from either inside
the parallel task, or the code that executes after the parallel task, making it easy to call more than one thread or 
to make a pipeline parallel to the main pipeline.

### Precautions

The only problem with the parallel tasks is that code related to OpenGL, due to problems of implementation of OpenGL, 
can not be executed in parallel (the context of OpenGL only lives in the main thread). And due to this, all the calls
to OpenGL must be executed either on the main thread directly, or in a function `then`.

When programming a new thread task, be aware that the function or method must receive a function (preferably in a 
parameter called `then`) and must execute that function at the end of the parallel routine. This because usually the
thread tasks tend to "accumulate" (callback hell), so if in one of those calls the `then` function is not called it
makes all the pipeline fail.

# Code Guidelines

- Identation must be of four spaces.
- Docstring must follow the google docstring format.
- Lines must be shorter or equal than 100 characters when possible.
- All files, clases, methods and functions must be documented.
- When possible, files should contain a small program inside the block `if __name__ == __main__` with an example of the methods and definition in the file.
- Method and function definitions must have the type of the parameters and the output using `typing` from python.