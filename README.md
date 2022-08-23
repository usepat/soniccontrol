# SONICCONTROL

SonicControl is a python based light-weighted graphical user interface for controlling a SonicAmp. The GUI uses can be run on any platform and uses the serial interface to communicate with the device. Furthermore, SonicControl offers a simple scripting language to control a SonicAmp automatically for a certain duration.

Here are some screenshots to get a better understanding:

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
- ```gain <percent>```
- ```hold <seconds or milliseconds>```
- ```on```
- ```off```
- ```startloop <number>```
- ```endloop```
- ```ramp <start Hz> <stop Hz> <resolution in Hz> <delay in s or ms>```

![alt text](docs/pictures/scriptingtab.png)

#### Infotab and Serial-Monitor
The infotab gives you access to a help page document for further help for the application and tells you the version of the SonicControl itself. Likewise, the Serial Monitor gives you a quick briefing about possible commands to configure your SonicAmp.
![alt text](docs/pictures/infotab_serialmonitor.png)

## Installation
```bash
$ git clone https://github.com/usepat/soniccontrol.git
$ cd sonicontrol
$ python -m pip install -e .
```

## Usage
```bash
$ python -m soniccontrol
```

## Update
```bash
$ cd <path/to/soniccontrol>
$ git pull
$ python -m pip install -e .
```
