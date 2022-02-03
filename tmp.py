import sonicpackage as sp
from sonicpackage.data import Command, SonicAmp

connection = sp.connection.SerialConnection()
connection.initialize_amp()

Command.ramp(10000, 130000, 500, 100)
Command.hold(30)
Command.drink_beer(liter=4)



