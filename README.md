# SONICCONTROL

SonicControl is a python based light-weighted graphical user interface for controlling a SonicAmp. The GUI uses can be run on any platform and uses the serial interface to communicate with the device. Furthermore, SonicControl offers a simple scripting language to control a SonicAmp automatically for a certain duration.

## Installation

The installation of SonicControl is done by cloning the repository and installing the application while being in the folder through using the python package manager pip:
```bash
$ git clone https://github.com/usepat/soniccontrol.git
$ cd soniccontrol
$ python -m pip install -e .
```

## Update
To update soniccontrol, navigate to the cloned repository on your device and pull the new version. Proceed with installing the new souce code to the python path with using pip:
```bash
$ cd <path/to/soniccontrol>
$ git pull
$ python -m pip install -e .
```

#### Changing version
If you wish to change to a certain verison of the application, you can gladly do so by checking out the release and installing the source code to the python path using pip:
```bash
$ cd <path/to/soniccontrol>
$ git checkout <release tag>
$ python -m pip install -e .
```

## Usage
```bash
$ python -m soniccontrol
```

#### Writing a config file for soniccontrol ``config.json``
The GUI provides the posssibility to write a config file to set up some data, that the GUI should know for controlling a SonicAmp device. To be precise, the current configuration possibilities are:
- To set a hexflash flag, so that the user can flash and update the firmware for a SonicAmp system. Though this feature is not fully tested and should be worked on
- To set a development mode flag, so that a few buttons and features are seen, even without connecting to a SonicAmp system
- To give concrete data information about a transducer and it's charateristics
    - The name of the transducer
    - ATF1, ATF2 and ATF3 frequencies information
    - ATT1, ATT2 temperature information
    - A threshold frequency to set a threshold frequency between the MHz mode and kHz Mode
    - Some information, so that the user knows what transducer is currently configured and has a overview

The file ``config.json`` should be placed into the root directory soniccontrol, along with ``setup.py, requirements.txt, README.md`` and so on, or in case of a binary,
it should be placed into the same folder, where the ``.exe`` app is.
This data is provided in a certain format in a json file, according to json syntax rules. Here are some examples:
```json
{
  "hexflash": false, 
  "dev_mode": false,
  "transducer": {
    "<Name of first transducer>": {
      "atf1": 1000000,
      "atf2": 2000000,
      "atf3": 3000000,
      "threshold_freq": 1100000,
      "att1": 12,
      "att2": 50,
      "Comment": "Some comment so that I know what I am configuring",
      "Distance": "A Distance so that I know during the experiment what to do"
    },
    "<Name of second transducer>": {
      "atf1": 1230984,
      "atf2": 3249080,
      "atf3": 5098234,
      "threshold_freq": 900000,
      "att1": 420,
      "att2": 187,
      "Comment": "I am a comment for you",
      "Distance": "To the moon and back"
    }
  }
}
```
Note that you can provide as much information and entries about the transducer as you want, the program doesn't care about anything.
In fact, it won't even care if you provide no information. The value will be just set to ``None``. This will just result, that when you 
select a certain configuration of a transducer the program will send a command to the device with the value ``None``. This won't change
anything.

Another example:
```json
{
  "transducer": {
    "<Name of first transducer>": {
      "atf1": 1000000,
      "atf2": 2000000,
      "atf3": 3000000
    },
    "<Name of second transducer>": {
      "atf1": 1230984,
      "atf2": 3249080,
      "atf3": 5098234,
    },
    "<Name of third transducer>": {
      "atf1": 3498573,
      "atf2": 4596873,
      "atf3": 982734
    },
    "<Name of fourth transducer>": {
      "atf1": 2938742,
      "atf2": 6000000,
      "atf3": 1987989,
    }
  }
}
```
All other configurations are settet to ``None`` or their default value, like ``hexlfash``, ``dev_mode`` and ``threshold_freq``.
Please be aware, that the naming of all those values is very strict. ``Threshold Frequency`` won't do anything, you should use ``threshold_freq``.

#### Connectiontab
The connection tab is the interface you are greeted with, here you can connect to a SonicAmp and inspect the already established connection.

![alt text](docs/pictures/connectiontab.png)

#### Hometab
The home tab is the main interface to control a SonicAmp manually. Here you can set certain values and validate, that everything works fine. Additionally, here lies the button to take you to the SonicMeasure window or to open the Serial Monitor for configuring your SonicAmp through a command-line expirience.

![alt text](docs/pictures/hometab.png)

#### SonicMeasure
The SonicMeasure window is used to collect data regarding the electrical signature of a SonicAmp through-out a certain time in a configured range of frequencies. Each data point that was collected is instantly being plotted.

![alt text](docs/pictures/sonicmeasure.png)

#### Scriptingtab
The scripting tab is used to automate certain repetetive behaviours of a SonicAmp. The script language is relatively simple and easy-to-learn. There is a Scripting Helper, that shows the behaviour of each command. Nevertheless, here is a short documentation about this:

###### Commands:
- ```frequency <Hz>```
  
  Sets the frequency of a SonicAmp to the passed number, if it is possible

- ```gain <percent>```

  Sets the gain of a SonicAmp tp the passed number, if it is possible

- ```hold <seconds or milliseconds>```
  
  Holds the state of things for the passed amount of time. The time unit defaults to milliseconds, whereas if you pass the time unit explicitly, seconds can be used:
    - ``hold 10s`` -> holds for 10 seconds
    - ``hold 100ms`` -> holfs for 100 milliseconds

- ```on```

  Turns the SonicAmp ultrasound signal output to ON

- ```off```

  Turns the SonicAmp ultrasound signal output to OFF

- ```startloop <number>```

  Declares the beginning of a loop with the passed quantifier, that declares how much cycles should the loop have

- ```endloop```

  Declares the end of a loop, it is mandatory for every loop to have an ``endloop`` statement

- ```ramp <start Hz> <stop Hz> <resolution in Hz> <delay in s or ms>```

  Sets a certain range of frequencies to the SonicAmp, starts with the ``<start Hz>`` parameter, goes until the ``<stop Hz>`` parameter and goes in ``<resolution in Hz>`` big steps. Furthermore, it waits ``<delay in s or ms>`` between the settings of frequencies. The delay paramter behaves like a hold parameter, so the time unit can also be passed.

![alt text](docs/pictures/scriptingtab.png)

#### Infotab and Serial-Monitor
The infotab gives you access to a help page document for further help for the application and tells you the version of the SonicControl itself. Likewise, the Serial Monitor gives you a quick briefing about possible commands to configure your SonicAmp.

![alt text](docs/pictures/infotab_serialmonitor.png)
