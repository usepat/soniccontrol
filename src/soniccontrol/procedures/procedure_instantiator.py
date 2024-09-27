from typing import Dict, Optional
from soniccontrol.procedures.procedure import Procedure, ProcedureType
from soniccontrol.procedures.procs.auto import AutoProc
from soniccontrol.procedures.procs.ramper import Ramper, RamperLocal, RamperRemote
from soniccontrol.procedures.procs.scan import ScanProc
from soniccontrol.procedures.procs.tune import TuneProc
from soniccontrol.procedures.procs.wipe import WipeProc
from soniccontrol.sonic_device import SonicDevice


class ProcedureInstantiator:
    def instantiate_ramp(self, device: SonicDevice) -> Optional[Ramper]:
        if device.has_command("!swf="):
            return None # Transducers that have switching frequencies cannot execute the ramp
        elif device.has_command("!ramp"):
            return RamperRemote()
        else:
            return RamperLocal()
        
    def instantiate_procedures(self, device: SonicDevice) -> Dict[ProcedureType, Procedure]:
        procedures: Dict[ProcedureType, Procedure] = {}

        ramp = self.instantiate_ramp(device)
        if ramp:
            procedures[ProcedureType.RAMP] = ramp

        if device.has_command("!scan"):
            procedures[ProcedureType.SCAN] = ScanProc()

        if device.has_command("!auto"):
            procedures[ProcedureType.AUTO] = AutoProc()

        if device.has_command("!tune"):
            procedures[ProcedureType.TUNE] = TuneProc()

        if device.has_command("!wipe"):
            procedures[ProcedureType.WIPE] = WipeProc()

        return procedures
        


