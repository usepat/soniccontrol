# Procedures

## Brief Description

Procedures are little programs that have a predefined process, that can be adjusted by parameters.  
They set the gain and frequency on the device.

## Use Cases

Some of them are for tuning(adjust frequency), ramping (go through a range of sequences), scaning(find the peak frequency).  
The user can define the parameters of the procedure (how long a single step takes, for example).  
The user can select which procedures to run and can start and stop them.  
A procedure is basically a program. It can be included in a script.  
There should be a control panel widget, that shows which procedures are available on the device and which not. This panel should also show which parameters are set for these procedures and which one is running.

## Requirements

Some procedures are available on the device and can be run there directly. If the device does not have the procedure, than the procedure should instead run locally on the controller computer and just send the instructions to the device. So basically like a script.  
When a remote procedure is run, we do not know the state of the procedure, but we can get notify messages from the device, that can contain such information.
The communication could become a bottleneck.

## Implementation

On construction of the sonic amp in the sonic amp builder, we look if we get back with `?list_commands` a list that contains our procedure. Like that we can check, if the device has the procedure.  
We make a procedure instantiator, that checks on the sonic amp if it has the procedure. Internally the procedure instantiator gives back than either a remote or local procedure. Both have the same interface so they can be interchanged easely.  
