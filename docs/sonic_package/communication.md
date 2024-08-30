
@defgroup Communication
@ingroup SonicPackage
@addtogroup Communication
@{

# Communication {#Communication}

## Brief Description

SonicControl communicates with the device connected to the computer.

@startuml
!include sonicpackage/class_communication.puml
@enduml

## Connection

The connection is established by the [ConnectionFactory](@ref sonicpackage.communication.connection_factory.ConnectionFactory) and can either be to a serial port or to a process (that simulates the device).
In future also a connection with tcp or udp over a server could be added. 

## Protocol

@subpage PackageProtocol

We made a custom protocol to send the commands and device logs.
The protocol is defined like that that single packages are always send, instead of single commands directly. This offers more flexibility.
In the code the protocol is encapsulated in the [SonicProtocol](@ref sonicpackage.communication.sonic_protocol.SonicProtocol) class.
This class gets used by the Communicator and PackageFetcher to read and send messages.

## Communicator

@see sonicpackage.interfaces.Communicator

The Communicator is responsible for establishing and also putting down a connection with the [ConnectionFactory](@ref sonicpackage.communication.connection_factory.ConnectionFactory).
Over the Communicator Commands can be send and answers received. It offers mainly two methods for that:
- [send_and_wait_for_answer](@ref sonicpackage.interfaces.Communicator.send_and_wait_for_answer): for sending a command an getting the corresponding answer
- [read_message](@ref sonicpackage.interfaces.Communicator.read_message): for fetching whatever message just got read by the Communicator
So we have a method that pushes and waits and a method for pulling.

### New Communicator

The new communicator uses internally a [PackageFetcher](@ref package_fetcher.PackageFetcher) that runs in the background and constantly reads packages from the input stream.  
It also uses the new Package protocol, that is set up like that, that each command is send in a own package with an unique id and the package with the corresponding answer has the same id.
So we know exactly which answer belongs to which command and no race conditions what so ever can occur.

### Legacy

The legacy communicator just reads blindly the input line for line. Very error prone.

### Determining which one to use

The [CommunicatorBuilder](@ref sonicpackage.communication.communicator_builder.CommunicatorBuilder) tries out to establish a connection with both versions and then uses the one that works and returns it.

@}