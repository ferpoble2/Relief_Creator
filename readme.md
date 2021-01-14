# Relief Creator

Simple application to modify terrain using poligons and functions over the points of the terrain.

# Context of the application

This project is development as a thesis project for the Computer Science department of the University of Chile and
consist on a program that is able to modify the height of geographical data using interactive controls to draw polygons
in the screen.

It is developed with the goal of making easier to modify the height of maps, without the necessity of using software or
tools not developed for that purpose.

# Usage

## How to use the platform

### Shortcuts

This is a list of shortcuts implemented in the program to make the usage of it more fast.

- CTRL + O: Load a netcdf file on the program.

# Instructions for developers

To install the dependencies of the program run the following command in the root folder of the project:

    pip install -r requeriments.txt


To execute the program run the following command in the same folder:

    python ./src/main.py

It is recommended to use a virtual environment to install the dependencies: https://docs.python.org/3/tutorial/venv.html

# How to build

The application can be built using the command `auto-py-to-exe` (or the equivalent `make build-executable`) and then 
importng the file `build_conf.json` that is on the root of the project.

The command opens a window application where one can configure how to create a .exe program from python, under the
settings tab one can import a configuration file, there is where the file `build_conf.json` must be imported.

After that just press the button at the end of the GUI application to generate the program.

The program is located in the `output` folder under the name of ReliefeCreator.

# Tools

There is a number of tools that form part of the engine, they are stored as strings by the program class. Here is the list of all tools of the program:

- move_map: Tool that is active when moving the 2D map on the engine.

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