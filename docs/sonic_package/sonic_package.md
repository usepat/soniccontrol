@defgroup SonicPackage
@addtogroup SonicPackage
@{

# SonicPackage {#SonicPackage}

## Brief Description

@see sonicpackage

SonicPackage is the core of SonicControl.
It contains all necessary functionality to communicate with the device, send commands and get answers, execute scripts and execute procedures.

@startuml
!include sonicpackage/class_sonic_package.puml
@enduml

## Sonic Amp

@see sonicpackage.sonicamp_.SonicAmp

The SonicAmp is responsible for executing commands and then updates the [Status](@ref sonicpackage.amp_data.Status) of itself. It basically represents the device and hides all the communication that occurs under the hood, so that you can program, like you execute commands on the device directly.  
The amp has to be constructed with the [AmpBuilder](@ref sonicpackage.builder.AmpBuilder) after constructing the [Communicator](@ref sonicpackage.communication.communicator.Communicator).

## RemoteController

@see sonicpackage.remote_controller.RemoteController

The RemoteController provides a class that encapsulates everything. From accessing and setting attributes like frequency, to executing scripts and commands. 
It is used by @ref sonic_robot that is a library for the RobotFramework and basically just wraps the RemoteController.  
Also it will be used by the @ref soniccontrol_cli.

@}