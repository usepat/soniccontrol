from typing import Optional
from sonicpackage.procedures.ramper import Ramper, RamperLocal, RamperRemote
from sonicpackage.sonicamp_ import SonicAmp


class ProcedureInstantiator:
    def instantiate_ramp(self, device: SonicAmp) -> Optional[Ramper]:
        if device.has_command("!swf="):
            return None # Transducers that have switching frequencies cannot execute the ramp
        elif device.has_command("!ramp"):
            return RamperRemote()
        else:
            return RamperLocal()

