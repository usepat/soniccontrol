from typing import Dict, Optional
from sonicpackage.procedures.procedure import Procedure, ProcedureType
from sonicpackage.procedures.procs.auto import AutoProc
from sonicpackage.procedures.procs.ramper import Ramper, RamperLocal, RamperRemote
from sonicpackage.procedures.procs.scan import ScanProc
from sonicpackage.procedures.procs.tune import TuneProc
from sonicpackage.procedures.procs.wipe import WipeProc
from sonicpackage.sonicamp_ import SonicAmp


class ProcedureInstantiator:
    def instantiate_ramp(self, device: SonicAmp) -> Optional[Ramper]:
        if device.has_command("!swf="):
            return None # Transducers that have switching frequencies cannot execute the ramp
        elif device.has_command("!ramp"):
            return RamperRemote()
        else:
            return RamperLocal()
        
    def instantiate_procedures(self, device: SonicAmp) -> Dict[ProcedureType, Procedure]:
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
        


