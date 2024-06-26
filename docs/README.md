# Setup Soniccontrol

## Get the sourcecode

Make sure to clone the repository via [Git](https://www.git-scm.com/) or download the sourcecode under the [Github Page](https://github.com/usepat/soniccontrol).

## Install python

Install the right python version locally, so that you can run Soniccontrol. The current supported python versions are listed on the [Github Page](https://github.com/usepat/soniccontrol) or in the ./setup.cfg file in the root directory of Soniccontrol. 

## Virtual environemt

Open the root folder of soniccontrol with your terminal of choice and initialize a python virtual environment.

```
python -m venv .venv
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

## Installing Soniccontrol

In the created and activated virutal environment, the follwing command should be executed next.

```
pip install -e .
```

``pip`` is the Python Package installer, whereas ``-e`` tells ``pip``, that the installed code should be editable. This results into python declaring the root sourcecode as the actual application. The user can edit the sourcecode and run python without reinstalling the application.

### Installing development libraries

To install development libraries, one should run the following command.
```
pip install -r requirements_dev.txt
```

This command installs all libraries listed in the file ``requirements_dev.txt``, which include libraries for testing and DevOps.

## Running Soniccontrol

To run soniccontrol, either run the ``__main__.py`` file within the editor like vscode or with the python command, or run the following command.
```
python -m soniccontrol
```
Due to the fact, that soniccontrol was installed as a python module. The user can start the application as a python module.