# Editor 

## Brief Description
s
The editor lets the user execute scripts to control the device.

# Use Cases

- The user can start and stop scripts.
- The user can step through scripts, like in a debugger
- The user can open a scripting guide
- The user can save and load script files. 

## Implementation

@see soniccontrol_gui.views.control.editor

### Running the Interpreter

To parse the script the [ScriptingFacade.parse_script](@ref sonicpackage.scripting.ScriptingFacade.parse_script) method is used, that returns an [Interpreter](ref sonicpackage.scripting.ScriptingFacade.Script). The Interpreter can be step through because it is an async iterator.

The Editor saves an instance of the Interpreter and runs the [interpreter_engine](@ref soniccontrol_gui.views.control.editor.Editor._interpreter_engine) to execute it. Separating the interpreter state from the interpreter execution has the advantage, that we can pause the execution without having to explicitly save the interpreter state and the same goes for continuing the execution.

### State Machine

There is a single method [set_interpreter_state](soniccontrol_gui.views.control.editor.Editor._set_interpreter_state) to handle and set in which state the interpreter is. This is important, to control the logic flow of the editor and to enable, disable the gui buttons for starting, stopping the interpreter.

@startuml
!include soniccontrol_gui/interpreter_state_machine.puml
@enduml

