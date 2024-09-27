# Welcome to the Help Page for SonicDevice Systems!

There are a variety of commands to control your SonicDevice under your liking. Typically, a command that sets up the SonicDevice System starts with an `<!>`, whereas commands that start with a `<?>` ask the System about something and outputs this data.

## Command List

| Command          | Description                                                                      |
|------------------|----------------------------------------------------------------------------------|
| `!SERIAL`        | Set your SonicDevice to the serial mode                                             |
| `!f=<Frequency>` | Sets the frequency you want to operate on                                        |
| `!g=<Gain>`      | Sets the Gain to your liking                                                     |
| `!cur1=<mAmpere>`| Sets the current of the 1st Interface                                            |
| `!cur2=<mAmpere>`| Sets the current of the 2nd Interface                                            |
| `!KHZ`           | Sets the Frequency range to KHz                                                  |
| `!MHZ`           | Sets the Frequency range to MHz                                                  |
| `!ON`            | Starts the output of the signal                                                  |
| `!OFF`           | Ends the Output of the Signal, Auto and Wipe                                     |
| `!WIPE`          | [WIPE ONLY] Starts the wiping process with indefinite cycles                     |
| `!WIPE=<Cycles>` | [WIPE ONLY] Starts the wiping process with definite cycles                       |
| `!prot=<Protocol>`| Sets the protocol of your liking                                                |
| `!rang=<Frequency>`| Sets the frequency range for protocols                                         |
| `!step=<Range>`  | Sets the step range for protocols                                                |
| `!sing=<Seconds>`| Sets the time the Signal should be turned on during protocols                    |
| `!paus=<Seconds>`| Sets the time the Signal should be turned off during protocols                   |
| `!AUTO`          | Starts the Auto mode                                                             |
| `!atf1=<Frequency>`| Sets the Frequency for the 1st protocol                                        |
| `!atf2=<Frequency>`| Sets the Frequency for the 2nd protocol                                        |
| `!atf3=<Frequency>`| Sets the Frequency for the 3rd protocol                                        |
| `!tust=<Hertz>`  | Sets the tuning steps in Hz                                                      |
| `!tutm=<mseconds>`| Sets the tuning pause in milliseconds                                           |
| `!scst=<Hertz>`  | Sets the scanning steps in Hz                                                    |

| Command          | Description                                                                      |
|------------------|----------------------------------------------------------------------------------|
| `?`     | Prints information on the progress State |
| `?info` | Prints information on the software |
| `?type` | Prints the type of the SonicDevice System |
| `?freq` | Prints the current frequency |
| `?gain` | Prints the current gain |
| `?temp` | Prints the current temperature of the PT100 element |
| `?tpcb` | Prints the current temperature in the case |
| `?cur1` | Prints the Current of the 1st Interface |
| `?cur2` | Prints the Current of the 2nd Interface |
| `?sens` | Prints the values of the measurement chip |
| `?prot` | Lists the current protocol |
| `?list` | Lists all available protocols |
| `?atf1` | Prints the frequency of the 1st protocol |
| `?atf2` | Prints the frequency of the 2nd protocol |
| `?atf3` | Prints the frequency of the 3rd protocol |
| `?pval` | Prints values used for the protocol |
