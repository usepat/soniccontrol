@defgroup ProcControlling
@ingroup SonicControlGui
@addtogroup ProcControlling
@{

# Proc controlling {#ProcControlling}

## Brief Description

Procedures are complex sequences of instructions. Some can be executed directly on the device and others in sonic control.

## Use Cases

There are different procedures for cleaning, tuning, scanning etc. The user should be able to select and execute them.

The new devices support to start procedures on them directly (Run on device). The old ones in contrast cant do that. So sonic control has to send single instructions to them (Run remotely).

## Implementation

@see sonicpackage.procedures.procedure.Procedure

The module [procedures](@ref sonicpackage.procedures) is responsible for instantiating and executing the procedures. More information on that can be found in [Procedures](#Procedures).  
The [ProcControlling Tab](soniccontrol_gui.views.control.proc_controlling.ProcControlling) is responsible for providing the GUI interface for selecting, starting and stopping procedures.

### Creating the Forms from the ProcedureArgs

The ProcControlling Tab gets the list of available procedures via the [Procedure Controller](sonicpackage.procedures.procedure_controller.ProcedureController). Then it creates a [ProcedureWidget](@ref soniccontrol_gui.widgets.procedure_widget.ProcedureWidget) for each procedure. The ProcedureWidget provide fields according to the definition of the procedure args class they get.  
If you change a field, it will internally update the args dict. Those dicts get stored in the [ProcControlling Model](@ref soniccontrol_gui.views.control.proc_controlling.ProcControllingModel) and are then used to create the Procedure Args.

@startuml
!include sonic_control_gui/proc_controlling.puml
@enduml

@}
