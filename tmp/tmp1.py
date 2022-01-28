from sonicpackage.connection import *
import time
import serial

Sonicserial = SerialConnection()
Sonicserial.auto_connect()
time.sleep(5)

answer = Sonicserial.ser.read_until(b'').rstrip().decode()
print(answer)

# while True:
    # serial.get_answerline()
