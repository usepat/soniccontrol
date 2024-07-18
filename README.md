# Setup Soniccontrol

## Get the sourcecode

Make sure to clone the repository via [Git](https://www.git-scm.com/) or download the sourcecode under the [Github Page](https://github.com/usepat/soniccontrol).

## Install python

Install the right python version locally, so that you can run Soniccontrol. The current supported python versions are listed on the [Github Page](https://github.com/usepat/soniccontrol) or in the ./setup.cfg file in the root directory of Soniccontrol. 

## Virtual environemt

Open the root folder of soniccontrol with your terminal of choice and initialize a python virtual environment.  
Note that the enviroment will have the same python version as the python interpreter you created it with. So choose a python interpreter with a version >= 3.10

```
python3.10 -m venv .venv
```

The -m flag tells, that one is using a *module* of python, ``venv`` on the other hand is the official python virtual environment module. The last ``.venv`` is the name of the created virutal environment. Keep in mind that ``python`` is the python interpreter with the correct version for soniccontrol.

### Activating the virtual environment

To actually tell python to run a virtual environment one should run the following command.

#### Windows
```
.\.venv\Scripts\activate
```

#### MacOS & Linux
```
source ./.venv/bin/activate
```
or
```
. ./.venv/bin/activate
```

After running the corresponding command, the user should see the terminal reacting somehow and telling that the virtual environment is activated.

In vscode you can also create a .env file with 
```
PYTHONPATH=./.venv/bin/python
```
This will set the path correctly

For deactivating the venv use `deactivate`

## Installing Soniccontrol

In the created and activated virutal environment, the follwing command should be executed next.

```
pip install -e .
```

``pip`` is the Python Package installer, whereas ``-e`` tells ``pip``, that the installed code should be editable. This results into python declaring the root sourcecode as the actual application. The user can edit the sourcecode and run python without reinstalling the application.

### Installing development libraries

To install development libraries, one should run the following command.
```
pip install -r requirements.txt
pip install -r requirements_dev.txt
```

This command installs all libraries listed in the file ``requirements_dev.txt``, which include libraries for testing and DevOps. The `requirements.txt` is for the necessary dependencies for the release to run.  

You can create a `requirements.txt` with `pip freeze > requirements.txt`

## Running Soniccontrol

To run soniccontrol, either run the ``__main__.py`` file within the editor like vscode or with the python command, or run the following command.
```
python -m soniccontrol
```
Due to the fact, that soniccontrol was installed as a python module. The user can start the application as a python module.

# Develop soniccontrol

## Developing software

### mypy

One of the best static type checker for python. It is recommended to at least try writing typed python code and check it trough mypy.
Mypy is available through different installations, depending on how one is writing code and using which software, but the official 
website is available [here](https://mypy-lang.org/). There is also a VSCode extension of mypy.

### black formatter

A very handy and simple formatter for python code. It is recommended to install [black](https://github.com/psf/black) and activate it in your editor. Specifically, so that black runs through your code everytime one is saving. This is also available in the VSCode extension store.

### Ruff Linter

[Ruff](https://docs.astral.sh/ruff/) is the new "state of the art" python linter written in rust, that is fast and helps to develop clean python code. It is very recommended to use it, along or by itself mypy. Ruff is also supported in VSCode.

## Project structure

The project structure of soniccontrol bases arround folders

- ### ./bin folder
  The ``bin`` folder is the folder for binaries and executables
- ### ./docs folder
  The ``docs`` is where all files regarding documentation should be located at
- ### ./resources
  The ``resources`` folder is for assets used by code (like pictures, fonts, etc...)
- ### ./tests
  Tests folder is for code, that tests the main code (unit tests, functional tests, etc...)
- ### ./soniccontrol
  This is the source folder of the repository. Her e lies the inherent code arround soniccontrol
  The folder structure of soniccontrol is split up into modules

## Notable files

- ``./pyproject.toml`` is mainly a configuration file that tells python software what to expect
  - For example software like mypy, flake8, etc are looking into this file for configurations
- ``./setup.cfg`` is the file specifying the python project
  - General information like authors, version, etc
  - build system
  - library dependencies
- ``./setup.py`` should be left blank
- ``./tox.ini`` is a configuration file for ``tox``, a github actions devops python program
- ``./requirements.txt`` is the old way of dealing with library dependencies
  - Used to create with ``pip freeze``, look it up online for more information on that topic
- ``./requirements_dev.txt`` is the library dependencies for developers of soniccontrol


## Code format

The code format and style guide is determined by the official [PEP](https://peps.python.org/pep-0008/) style guide. This style guide is automatically partially applied with python code formatters like [black](https://github.com/psf/black).

## Useful documentations

- [ttkbootstrap](https://ttkbootstrap.readthedocs.io/en/latest/)
- [attrs](https://www.attrs.org/en/stable/)
- [tkinter](https://tkdocs.com/shipman/index.html)
- [pyserial](https://pyserial.readthedocs.io/en/latest/pyserial.html)
- [Code refactoring](https://refactoring.guru/)
- [Linting guide for VSCode](https://code.visualstudio.com/docs/python/linting)
- [Formatting](https://code.visualstudio.com/docs/python/formatting)
- [Github automatic testing and deployment (github actions)](https://docs.github.com/en/actions/automating-builds-and-tests/building-and-testing-python)
- [pytest](https://docs.pytest.org/en/stable/contents.html)

# Building soniccontrol

## PyInstaller and AutoPy2Exe

This is quite the topic. Python has libraries, that transform python code into an executable binary for windows, macOS and linux. Most notably [PyInstaller](https://pyinstaller.org/en/stable/). It is a commandline application that builds an application based on a configuration. 

But there is a better wrapper around PyInstaller. [Auto-py-to-exe](https://pypi.org/project/auto-py-to-exe/) is a GUI wrapper for PyInstaller that can save configurations and reproduce the building process easily. Here are a few steps and tips for using that application.
- Script location, should be the main entry of soniccontrol. Usually it is the ``__main__.py`` file.
  - Keep in mind that this file is the only file that is being converted into a binary. Everything else is just a local python interpreter running code
- Use one-directory option, due to not having support for one-file with such a big project
- Do not forget to tick "Window based", if the application is shipped to production and clients
- Use "Additional files" to specify all other sources and files for the ``__main__.py`` file
- The ``--name`` option should be "SonicControl"
- Contents directory should be "." for specifying the root directory. This is an old-fashioned way to deal with things. Feel free to discover the new ways of specifying the contents directory

## Inno Setup

[Inno setup](https://jrsoftware.org/isinfo.php) is used to wrap an application with a main ``.exe`` entry point around the windows operating system. The result is a single ``setup.exe`` that installs the applications contents in the windows programs folder and adding the main binary to the path, using the usual windows setup wizard client.

There are a ton of tutorials and guides online to use Inno Setup
- a [youtube tutorial](https://www.youtube.com/watch?v=jPnl5-bQGHI)
- an [article](https://python101.pythonlibrary.org/chapter44_creating_an_installer.html)

Of course there are many ways to convert python code into a binary application. Feel free to use your own way, just make sure that the application can start from every place (current working directory) and that everything runs as expected.

## Continious Deployment

On github there is set up a continious deployment that builds an exe and installer for windows. The code is in `.github/workflows/deploy.yml` and in the `scripts` folder.  
The generated files are uploaded on github as artifacts. You can go to them by going to the actions tab and then clicking on the runned workflow instance.
 