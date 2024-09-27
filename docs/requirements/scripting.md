## Scripting

The scripting functionality in the SonicControl application allows the user to recreate a certain state of the SonicDevice for a certain duration of time. It is one of the most powerful features in the application and is used by clients as well as by ourselves. It is needed for data collection and lab experiments. Using the scripting functionality consists of, as the name says, writing commands in a sequential manner and then executing those commands in the written order.

### Syntax of the scripting language

Historically there are the following commands in the grammar of the scripting language:
- ``frequency 1000000`` (same as ``!f=1000000`` in SonicDevice commands)
- ``gain 100`` (same as ``!g=100``)
- ``on`` (turns the signal on, same as ``!ON``)
- ``off`` (turns the signal off, same as ``!OFF``)
- ``auto`` (turns on the auto mode, or the default procedure of the sonicamp, same as ``!AUTO``)
- ``startloop 3`` (starts a loop block that is executed 3 times)
  - Declares the start of a loop block. After the statement, an optional number defines how many times the block should be executed. If left blank, the loop block becomes a "while true loop"
  - A loop block can be nested in another loop block
- ``endloop`` (ends a loop block)
- ``hold 5ms`` (holds the state of the SonicDevice for a certain duration of time)
  - The argument for the hold command defines the time duration that shall be held on to.
  - If argument has only a number, it defaults to seconds.
  - Otherwise, 100ms are milliseconds, 1s is one second.
  - Keep in mind, that a script that only holds, is unnessecary
- ``ramp 1000000 2000000 1000 100ms 100ms``
  - ramp \<start freq> \<end freq> \<step freq> \<hold during ON signal> \<hold during OFF signal>  
  - The hold arguments behave the same as the hold argument

!! IMPORTANT !!
Regardless of the commands that the scripting functionality gives, it should always support the firmware commands of the SonicDevice. So for instance a script with ``!f=1000000`` should also work.

#### Other alternatives and thoughts about the syntax

There were disscussions about changing the grammar of the scripting language to be more scalable in the future and/ or support a standartized language. This discussions unfortunately never ended with an satisfying result. Nevertheless, it is surely not a bad idea to think about the grammar and maybe design it so, that there won't be any scale issues in the future.

### Requirements

- [ ] The user can write a script.
- [ ] The user can save the script locally.
- [ ] The user can load the script from a local file.
- [ ] When the user starts the script, the UI changes, indicating that the script started
  - [ ] During that process, the current line the interpreter is at is highlighted, so that the user what part of the script is currently running.
  - [ ] During that process, the UI shows the current task of the interpreter. Such as "Setting frequency to 100 kHz".
- [ ] Before starting the script, all commands evaluated so that the approximate time duration of the whole scipt is calculated and shown in a progress bar.
  - [ ] If this is not possible, SonicControl defaults to a ``indeterminate`` progressbar.
- [ ] All needed commands are implemented
- [ ] The script supports variables
  - [ ] The scipt supports SonicDevice variables
    - For example ``variable=?atf1`` (give me the number that the sonicamp understands as ATF1)
- [ ] The script supports basic arithmetics
- [ ] Check with @TechHeadusePAT if ``if-else-conditions`` are wished to be part of the scripting language.
  - [ ] If so they should be implemented
- [ ] The scripting tab gives the user a wiki, to understand the commands and build a script by clicking the mouse.
- [ ] The user can pause the script and resume it. The script remembers what the last action was and where to resume.
- [ ] The script can sync with SonicMeasure, #80 
- [ ] A logging data file is generated, in which every command and interaction with the sonicamp is recorded and timestamped