# SonicControl

## What is SonicControl?

SonicControl was developed by [usePAT](https://www.usepat.com/) as a control software to interact with their ultrasonic cleaning devices (SonicDescale, SonicClean, ...).
With it you can:
- Communicate directly with the devices via a serial monitor
- Record measurements
- Execute predefined procedures
- Execute custom scripts
- Create settings and configurations for the devices
- Flash firmware on to the devices

usePAT decided to make SonicControl open source, so that users can adapt the software to their use cases.

## Quick Project Overview

The project contains multiple folders and files with each having a specific responsibility:
- *src*: In this folder is all the application code
- *docs*: In this folder lays the documentation pages
- *scripts*: Helper scripts for building, packaging, etc.
- *tests*: unit tests with pytest
- *robot_tests*: system tests with robot framework
- *.vscode*: settings, tasks, etc. for vscode
- *.github*: Workflows for github actions, settings and other stuff related to github
- *pyproject.toml*: Contains meta data and settings for the python project
- *requirements.txt*: Contains the dependencies of this project 

The project is divided into single python packages in the *src* folder:
- *soniccontrol*: Is the core package, that contains the logic for the communication with the device, executing scripts and flashing.
- *soniccontrol_gui*: This package contains the main application. It is a user friendly GUI.
- *soniccontrol_cli* **Work in progress**: This is a cli version of soniccontrol.
- *sonicprotocol* **Work in progress**: This package contains preprocessor scripts to generate html, c++ and python code for the custom protocol used by the software and the devices to communicate with each other.
- *sonic_robot*: This package is a library for the robot framework. It is used for system testing.
- *sonic_test_parrot* **Work in progress**: This is a custom testing program that works with recorded logs. 

Please read the rest of the documentation for a better understanding on how everything works and fits together.

## Installation Instructions for SonicControl(with pip)

### Prerequisites

First, ensure you have **Python 3.10** or newer installed.

#### On Windows:

- You can download the latest Python installer from [python.org](https://www.python.org/downloads/).
- If you don't want to override your current Python installation, make sure to **uncheck "Add to PATH"** during installation. After installation, you can create and manage virtual environments using `py`.

#### On Linux:

- You can install Python 3.10 using the apt package manager:

  ```bash
  sudo apt install python3.10
- To manage multiple Python versions, you can use Linux alternatives or pyenv to switch between versions.


## Get Started 

For the setup please look at [Get Started](@ref GetStarted).
Or give you the full experience with [Project Setup](@ref ProjectSetup).  

> Btw, those links will only work after building the documentation. 
> If you have not builded the documentation yet use this [link](./docs/get_started.md) instead.


