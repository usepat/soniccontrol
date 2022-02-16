import sonicpackage as sp

sonicamp = sp.SonicCatch.start()
sonicamp.set_frq(1200000)
sonicamp.set_mhz()
sonicamp.set_signal_on()
print(sonicamp.get_gain())
sonicamp.serial.disconnect()