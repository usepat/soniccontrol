## Serial Monitor

The serial monitor of SonicControl is a console window that can send string commands to a SonicAmp system. Simultaneounsly, answers and data coming from the connected device is logged and presented to the user. The whole serial monitor is inspired and leaned on the serial monitor from the [Arduino IDE](https://www.arduino.cc/en/software/).

### Requirements

- [ ] The user can send string messages to the device
  - [ ] After a message was sent. The message is presented in the output window like in a CLI application.
- [ ] After a message was sent, an answer to that message is received and presented in the ouput window.
- [ ] The user can activate an "Auto Read" checkbutton
  - [ ] If the checkbutton was checked, the Serial Monitor automatically reads all data from the SonicAmp and logs it in the output window
- [ ] If the user couldn't connect to a SonicAmp, but a connection is still possible, SonicControl goes into "Rescue mode"
  - [ ] The "Rescue Mode" is SoniControl presenting the user only the connection page and the Serial Monitor, so that the user, despite not having the full features, can communicate and control a SonicAmp system
