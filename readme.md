# Relief Creator

This repository presents a multiplatform and open-source software with an intuitive GUI to combine different paleoDEMs (Paleo Digital Elevation Models) and change elevations helping scientists to create and modify DEMs, maps that are critical for the understanding of the Earth System. While the program's focus is to modify DEM in the context of the study of palaeogeography, other disciplines that need to modify DEMs can also benefit. The software is written in Python, using OpenGl and multiple Python libraries.

# Usage

## How to use the program

### Shortcuts

This is a list of shortcuts implemented in the program to make the usage of it faster.

- CTRL + O: Load a netcdf file on the program.
- CTRL + T: Loaf a ctp file on the program.
- CTRL + Z: Undo the last action (Not implemented in all tools).
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

    pip3 install -r requeriments.txt

To execute the program, first you need to add the root directory to the PYTHONPATH variable, in windows, in a console CMD run the following command in the root directory of the project:

	set PYTHONPATH=.

In a system with Linux distribution run the following command:

	export PYTHONPATH=.

If you use a mac, run the following command:

	export PYTHONPATH="."

Then, to execute the program run the following command:

    python3 src/main.py

It is recommended to use a virtual environment to install the dependencies: https://docs.python.org/3/tutorial/venv.html

(If you use windows and use a virtual environment called *venv* then running the command `make run-windows` will run the
project, it is necessary to have make for windows installed)

# How to build

The application can be built using the command `auto-py-to-exe` (or the equivalent `make build-executable-windows`) and then importing the file `build_conf.json` located on the root of the project. Make sure to create a virtual environment with python and install all the dependencies from the file `requeriments.txt` before launching the program.

The command opens a window application that allows the configuration of the process to create a .exe program from the python source code. 

In the settings tab of the program there is a menu that allows the import of previously generated configuration files. The file `build_conf.json` must be imported in this section of the program, loading all the configuration to generate the executable of the program.

To build the executable, the program needs the absolute path of the files that it will be using, and thus, before
running the program, it is necessary to replace all the paths that contains `<project_directory>` with the absolute path
where the project is located.

After configuring the program, pressing the button at the end of the program will start the process to generate an
executable.

The program will be generated in the `output` folder under the name of ReliefCreator.

NOTE: After the configuration of the program, at the end of all the options, there will be a textbox with a command,
this command can be used to generate the executable from a terminal without using the program.

## Using the console

If you want to build the application using the command line, then run the following command with the virtual environment of python activated:

```bash
pyinstaller --noconfirm --onedir --console --icon "<project_directory>/resources/icons/program_icons/icon_program.ico" --name "ReliefeCreator" --add-data "<project_directory>/resources/logs/;resources/logs/" --add-data "<project_directory>/resources/colors/;resources/colors/" --add-data "<project_directory>/resources/sample_netcdf;resources/sample_netcdf" --add-data "<project_directory>/venv/Lib/site-packages/glfw/glfw3.dll;." --add-data "<project_directory>/venv/Lib/site-packages/glfw/msvcr110.dll;." --hidden-import "cftime" --add-data "<project_directory>/resources/fonts;resources/fonts" --add-data "<project_directory>/src/engine/shaders;src/engine/shaders/" --add-data "<project_directory>/resources/icons;resources/icons" --add-data "<project_directory>/resources/sample_polygons;resources/sample_polygons" --hidden-import "skimage.filters.rank.core_cy_3d"  "<project_directory>/src/main.py"
```

Make sure to change all strings that contains `<project_directory>` with the absolute path of the directory in which the project  is stored.

# How to change the icon of the application

## Window icon

The icon showed on the window application (the one showed in the top-left corner of the program) is stored
in `resources/icons/program_icons/icon_program.png`.

The logic to set the icon is implemented in the method `initialize` of the class `Engine`. It uses the
method `set_window_icon` of the `glfw` library to do it.

To change the icon of the program is enough to change the old file with a new one of the same format (PNG). 

Please consider that the image used must have RGBA channels to work.

## Application icon

The icon showed on the application executable (and the one that the OS will use to show on other programs) is stored in `resources/icons/program_icons/icon_program.ico`.

This icon is set on the program on the building process, and thus, there is no logic code related to it.

On the building of the application, in the windows that opens when running `auto-py-to-exe`, there is a section called ICON that allows to select an icon to use for the program. To change the icon used in the program just select another file on the icon section or change the already existent one with another file with the same name and extension.

Please consider that all the application icons must be in format `ICO`.

# How to run tests

The project includes inside the folder `test` different types of tests that check the functionality of the program. These tests were written using the unit tests library of the Python language.

To run the tests, add the root directory of the project to the PYTHONPATH variable and then execute the following command inside the root folder of the project:

```
python -m unittest discover .\test
```

This will run all the tests inside the folder `test`.

All the dependencies of the project must be installed for the tests to run correctly.

# Tools

There is a number of tools that form part of the engine, they are stored as Enum by the program module. Here is the list
of all tools of the program:

|       ID       |                        Description                        |
| :------------: | :-------------------------------------------------------: |
|    move_map    | Tool that is active when moving the 2D map on the engine. |
| create_polygon |          Tool to create polygons on the screen.           |

Only one tool can be active at a given time.

Note: The name from above is not showed in the tools frame of the program but is the one used by the program internally. The list of all tools is defined inside the program module.

# Filters

There is several filters that can be applied to the transformations before modifying the points of the loaded models,
they are given to the transformations inside a list. Here are all filters implemented currently in the program:

|         ID          |     Parameters      |                         Description                          |
| :-----------------: | :-----------------: | :----------------------------------------------------------: |
|  HeightLessThan   |        float        | Filter all points with height less than the specified value. |
| HeightGreaterThan |        float        | Filter all points with height greater than the specified value. |
|        IsIn        | string (polygon id) | Filter all the points that are inside the specified polygon. |
|      IsNotIn      | string (polygon id) | Filter all the points that are not in the specified polygon (are outside the polygon). |

The transformations are the one in charge of getting all the necessary information to apply the filters correctly over
the transformation zone.

Note: The filters are defined inside the filter module, which is inside the scene module.

# How to extend the program with new functionality

## How to create new frames on the application

The program uses PyIMGUI to define the GUI of the application. This is a library that allows to create easy menus, buttons and other GUI elements in applications that use OpenGL. The documentation about how to use it can be found in the following link https://pyimgui.readthedocs.io/en/latest/reference/imgui.core.html.

The GUIManager class is the one who controls all the GUI elements, this one is the responsible for the management of the
different windows and frames that the application uses.

All windows showed in the application, either in 2D mode or 3D mode, are instances of the Frame class or a class that
inherit from it. All classes that inherit from the Frame class must define the render method. This method is called from
the GUIManager in the context of rendering the IMGUI frames each frame, updating the GUI of the application.

To extend the functionality of the application with a new window or button, one must create or modify a class that
inherit from the Frame class and define the rendering process that must be executed in every frame. The rendering must
use the IMGUI functions to create windows on the program and buttons.

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

The GUIManager, and all the components of the application, get the data from the Engine component. To keep the program organized, all frames must get the data that they need from the GUIManager class. The GUIManager is the one that should ask the information to the Engine component.

The engine, as the center of the program, can get the data from all the other components by calling the methods that
they have defined.

Most of the data can be obtained using the already defined methods on the engine, but if you want to update the program
with new functionality, then you must define the method to get the data in the respective component, and then have the
engine call that method to get the data. This way the components remain organized while still independent of each other.

To see a diagram with all the components of the program, see the diagram generated by PlantUML located
at `docs/objects/main_objects.puml`.

## How to add new functionality to the program

How to add new functionality depends on the functionality to add to the program, depending on the type of functionality to add it must be added in a different component or class.

The components and the type of functionality expected in their interior are defined as follows:

+ Scene: Functionality related to the maps, 2D or 3D, and the modifications that happens to them and the polygons.
+ GUI: Functionality related to the UI of the program.
+ Render: Functionality related to the rendering process and the main cycle of the program.
+ Controller: Functionality related to the keyboard/mouse input and how the program must answer to the events.
+ Program: Functionality related to the state of the program in each moment.
+ Engine: Functionality related to the communication of different components of the program, how the program must answer possible errors that happens and related to the threads and execution of tasks.
+ Output: Functionality related to the generation of output files.
+ Input: Functionality related to reading of input files.

Each component is composed of one packager than can or cannot have more sub-packages in its interior.

Once located where the functionality to add should be, there are two things to consider:

1. The functionality must be called from the engine.
2. The possible errors that can happen with the functionality must be handled by the engine.

The functionality defined in the components must be called by the engine, this is to keep the code organized and
object-oriented, allowing to change the code inside the components while keeping the same API on the engine.

The second point is related to the first and is to keep the error handling process the more organized possible, being
the engine the one in charge of handling all possible errors that happens with the program.

## Example

So, for example, if there is the need to add a new functionality to apply a filter to the full map when the user presses
a button, then the following steps should be done to add that functionality to the program:

1. Locate in which component the functionality should be added (in this case, it must be added on the Scene component,
   in the module map_transformation).

2. Implement the functionality in the given component, either modifying an existent class or creating a new one, and add
   a method that allows to use the functionality to the class that is connected to the engine (in this case, add a new
   class that do the required logic).

3. Implement a new method in the engine class where the new functionality is called and all the possible errors are
   handled. (in this case, the method `apply_map_transformation` is already defined)

This should be the end of a normal process, in the current example we still need to add a button to connect the
functionality implemented to the GUI.

4. Create a new class that inherit from the Frame class or modify an already existing frame and add the button.

5. Define in the GUIManager class a method that calls the method defined previously in the Engine.

6. Make the added button call the method defined in the  GUIManager to run the functionality when it is pressed.

The order in which the functions are called to run the logic is as follows at the end: Frame=>GUIManager=>Engine=>Scene

In this example, we needed to modify not just the Scene and the Engine but also the GUI to trigger the functionality.
This does not have to be always the case, the functionality can be triggered also by events, in which case the
Controller must be modified or by an action made by another component.

To keep things organized and OOP, all functionality of a component that call functionality located in another component must be called using the engine.

# About the controller

The program uses two types of controllers to manage the input from the user, one is the controller that the
library `imgui` uses to process the inputs of the user related to the GUI, and the other is the one stored in the
class `Controller`.

Both controllers are used in the program, the controller stored in the class `Controller` is the one in charge of
calling the controller from `imgui`whenever is necessary.

# About the camera

For the 3D rendering, the program uses a 3D camera that uses spherical coordinates.

In this program, the coordinates used are (r,phi,theta), where the phi angle correspond to the azimuthal angle (parallel to the xy plane) and the theta angle correspond with the elevation angle.

Something to consider is that the elevation angle (theta) starts from the top, this means that the point (1,0,0) in spherical coordinates correspond to the point (0,0,1) in cartesian coordinates.

# Reading NetCDF files

The file `src/input/NetCDF.py` is the one in charge of reading the files in format NetCDF and generate numpy arrays.

To achieve this, the program reads the contents of the file using the NetCDF4 library. That generates dictionary-like
object with the data of the file, then, the program search in the dictionary for the keys that have information about
the latitude, longitude and height.

## How to add more keys to search for in the netcdf files

If at some point, in the moment of loading a file the program hits a KeyError, then is highly probable that the netcdf file have keys with another name that the ones the program uses.

The keys that the program uses for the longitude, latitude and height are stored in the files `longitude_keys.json`, `latitude_keys.json` and `height_keys.json` respectively inside the folder resources.

To add a new key, just modify the files listed before with the new key that you want the program to read.

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

In the file `src/utils.py` are defined the following variables that modify the behavior of the loggers:

- LOG_TO_FILE: If logging or not to a file
- LOG_TO_CONSOLE: If logging or not to the console
- LOG_LEVEL: Log level to use for the logs
- LOG_FILE_LEVEL: Log level to use to log in the files
- LOG_ONLY_LISTED_MODULES: If log only listed modules or log every module
- LOG_LIST_MODULES: List of modules to log if LOG_ONLY_LISTED_MODULES is true

# About the parallel tasks on the engine

The engine has implemented two main pipelines to delegate tasks to sometime in the future, tasks and parallel tasks.

## Tasks

Tasks are code that will be executed after some numbers of frames have passed, this is, the code executed will be delayed some number of frames.

The `engine`, at the beginning of each frame, checks if there is pending tasks to execute, if there is, then checks if
the frame count of them is Zero, if it is, then the engine executes the code, if not, then the engine subtracts 1 from
the frame count.

This method of executing tasks in the future is used when executing a task with loading frame on the program, since this
gives time to the frame to render and show before executing the task.

## Parallel tasks

Parallel tasks are code that will be executed in parallel along with the main pipeline of the engine, this is, will be
executed while the engine does the rendering of the application.

These tasks are executed in parallel using threads, and since threads share the memory and variables, it is recommended
to not do anything else when a thread is running something. (this can be achieved setting a load screen on the program
using the method `set_loading(True)` of the class `Program`).

To set a parallel task on the engine it is necessary to use the method `set_thread_task`, the first parameter of the
method ( `parallel_task` ) is the function to execute in parallel and the second parameter ( `then` ) is a function that
will be executed after the thread finish its execution. This last function will be executed in the main thread of the
application.

To achieve this, when a parallel task is settled, the engine stores the thread in an internal variable, and, in each
frame, the engine ask the thread if it finished its execution, if it finished, then the engine execute the function
given as second parameter, if not, then the engine does nothing.

The parameters of the method `set_thread_task` are called `parallel_task` and `then`, they are called that way to
emulate how threads work in the language Javascript. This implementation of parallel tasks is a bit difficult to work
with, but give a lot of benefits, first, it is possible to execute code after the threads ends, not having to implement
on every thread a mechanism to check if the thread ended, second, it is possible to set new thread from either inside
the parallel task, or the code that executes after the parallel task, making it easy to call more than one thread or to
make a pipeline parallel to the main pipeline.

### Precautions

The only problem with the parallel tasks is that code related to OpenGL, due to problems of implementation of OpenGL,
cannot be executed in parallel (the context of OpenGL only lives in the main thread). And due to this, all the calls to
OpenGL must be executed either on the main thread directly, or in a function `then`.

When programming a new thread task in a component of the program, be aware that the function or method must receive a
function (preferably in a parameter called `then`) and must execute that function at the end of the parallel routine.
This because usually the thread tasks tend to "accumulate" (callback hell), so if in one of those calls the `then`
function is not called it makes all the others functions to fail.

```python
class Scene:
    ...

    def paralel_task(self, ..., then):  # Important to receive a then function as parameter.
        ...

        def parallel_logic():
            ...

        def after_thread_logic():
            ...
            then()  # Important to call the then logic at the end of the logic defined to the method.

        self.engine.set_thread_task(parallel_logic, after_thread_logic())

    ...
```
