# Sonic Protocol for descale - v1.0.0.Release
## **3**: LIST_AVAILABLE_COMMANDS  
<u>commands</u>  

Command to get a list of available commands.  

### Command Names
`?list_commands` | `?commands`  
### Params
No parameters  
### Answer
- **list_commands**: *str*  
## **4**: GET_HELP  
<u>help</u>  

Command to get help information.  

### Command Names
`?help`  
### Params
No parameters  
### Answer
- **help**: *str*  
## **6**: GET_PROTOCOL  
  

...  

### Command Names
`?protocol`  
### Params
No parameters  
### Answer
- **device_type**: *DeviceType*  
	Possible values:  
	- unknown  
	- descale  
	- catch  
	- wipe  
	- mvp_worker  
- **version**: *Version*  
- **is_release**: *bool*  
## **20**: DASH  
<u>update</u> | <u>status</u>  

Mainly used by sonic control to get a short and computer friendly parsable status update.  

### Command Names
`-` | `get_update`  
### Params
No parameters  
### Answer
- **error_code**: *int*  
- **freq**: *int* in [kHz]  
- **gain**: *int* in [%]  
- **procedure**: *int*  
- **temp**: *int* in [C°]  
- **urms**: *int* in [uV]  
- **irms**: *int* in [uA]  
- **phase**: *int* in [u°]  
- **signal**: *bool*  
- **ts_flag**: *int* in [uV]  
## **40**: GET_INFO  
  

...  

### Command Names
`?info`  
### Params
No parameters  
### Answer
- **device_type**: *DeviceType*  
	Possible values:  
	- unknown  
	- descale  
	- catch  
	- wipe  
	- mvp_worker  
- **hardware_version**: *Version*  
- **firmware_version**: *Version*  
- **build_hash**: *str*  
- **build_date**: *str*  
## **50**: GET_FREQ  
<u>frequency</u> | <u>transducer</u>  

Command to get the frequency of the transducer on the device.  

### Command Names
`?f` | `?freq` | `?frequency` | `get_frequency`  
### Params
No parameters  
### Answer
- **freq**: *int* in [kHz]  
## **60**: GET_GAIN  
<u>gain</u> | <u>transducer</u>  

Command to get the gain of the transducer on the device.  

### Command Names
`?g` | `?gain` | `get_gain`  
### Params
No parameters  
### Answer
- **gain**: *int* in [%]  
## **70**: GET_TEMP  
<u>temperature</u> | <u>transducer</u>  

Command to get the temperature of the device.  

### Command Names
`?temp` | `?temperature` | `get_temperature`  
### Params
No parameters  
### Answer
- **temp**: *int* in [C°]  
## **1010**: SET_INPUT_SOURCE  
<u>communication</u>  

Command to set the input source. Where to get commands from  

### Command Names
`!input` | `set_input_source`  
### Params
- **input_source**: *InputSource*  
	Possible values:  
	- manual  
	- external  
	- analog  
### Answer
- **input_source**: *InputSource*  
	Possible values:  
	- manual  
	- external  
	- analog  
## **1050**: SET_FREQ  
<u>frequency</u> | <u>transducer</u>  

Command to set the frequency of the transducer on the device.  

### Command Names
`!f` | `!freq` | `!frequency` | `set_frequency`  
### Params
- **freq**: *int* in [kHz]  
	Frequency of the transducer  
### Answer
- **freq**: *int* in [kHz]  
## **1060**: SET_GAIN  
<u>gain</u> | <u>transducer</u>  

Command to set the gain of the transducer on the device.  

### Command Names
`!g` | `!gain` | `set_gain`  
### Params
- **gain**: *int* in [%]  
	Gain of the transducer  
### Answer
- **gain**: *int* in [%]  
## **1080**: SET_ON  
<u>transducer</u>  

Command to turn the transducer on.  

### Command Names
`!ON` | `set_on`  
### Params
No parameters  
### Answer
- **signal**: *bool*  
## **1090**: SET_OFF  
<u>transducer</u>  

Command to turn the transducer off.  

### Command Names
`!OFF` | `set_off`  
### Params
No parameters  
### Answer
- **signal**: *bool*  
## **1270**: SET_TERMINATION  
<u>communication</u> | <u>rs485</u>  

Command to set the 120Ohm termination resistor for rs485  

### Command Names
`!term` | `set_termination`  
### Params
- **termination**: *bool*  
### Answer
- **termination**: *bool*  
## **1290**: SET_PHYS_COM_CHANNEL  
<u>communication</u> | <u>protocol</u>  

Command to set the communication protocol  

### Command Names
`!prot` | `set_comm_protocol`  
### Params
- **communication_protocol**: *CommunicationProtocol*  
	Possible values:  
	- sonic  
	- modbus  
### Answer
- **communication_protocol**: *CommunicationProtocol*  
	Possible values:  
	- sonic  
	- modbus  
