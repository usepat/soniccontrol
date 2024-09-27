@defgroup Correspondence
@ingroup SonicControl
@addtogroup Correspondence
@{

# Correspondence

## Brief Description

This document describes how commands and answers are represented in code and how validation, construction, etc. works.

@startuml
!include soniccontrol/class_correspondence.puml
@enduml

## Commands {#Commands}

@see soniccontrol.command.Command

Commands consist of a command name and optionally a command argument. You can pass them a  [Communicator](@ref soniccontrol.communication.communicator.Communicator) instance on construction that they use when executed with [Command.execute](@ref soniccontrol.command.Command.execute) or you can pass a communicator in that function. Over the Communicator they pass the command as a message. 

Commands have one or more [CommandValidator](@ref soniccontrol.command.CommandValidator) to check and parse the response they receive by the Communicator. They have internally an answer struct that will then be set with the parsed result.

> Note: In Future there will be a refactor that will move the answer out of the command. Instead it will have a answer_factory method, and answer_validator for creating and then returning the answer

## Answers {#Answers}

@see soniccontrol.command.Answer

The answer of a command currently has a dictionary with the parsed results and also a bool that says if the answer is valid.
Also it stores the full original response of the Communicator.

> Note answer also contains an asyncio.Flag for knowing when the answer was received.
> This flag will be moved out to the Communicator in the future.

## CommandSet

The legacy protocol and the new protocol use different commands and also some commands that are the same, but have different responses. Our solution to that is by separating the commands into two distinct command sets.  
The [CommunicatorBuilder](@ref soniccontrol.communication.communicator_builder.CommunicatorBuilder) finds out which protocol gets used and returns depending on that the right Command Set and Communicator.

### Generating CommandSet and Commands via SonicProtocol

There is the plan to make a compiler that takes a definition of the sonic protocol and the device type and version as input and outputs the corresponding command set with the right commands. 
This would make the whole thing more flexible and extendable.
Also we could make two additional compilers.
- One for generating a manual in html
- Another on for generating the command and answer code for the firmware in C++
Like that it is also easier to manage up-to-dateness and consistency across those three projects. 

@}