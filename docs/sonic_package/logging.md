@defgroup Logging
@ingroup SonicPackage
@addtogroup Logging
@{

# Logging {#Logging}

## Use Cases

Logging is very important for every software. Logs can contain vital insights into the history of an application. This can be very useful for debugging. Image a client has a crash and you have no logs, that give you any hint of what happened.

## Implementation

Logging is implemented in sonic package like this that each class gets passed an instance of the callers logger and the class derives then its own logger from it.

Also the SonicControl GUI application creates an own logger for each connection. So you have normally something like `connection.class1.class2` as logger names, where class1 instantiated class2. For example `COM1.SerialCommunicator.PackageFetcher`.

The log files get written into a file with the same name as the connection normally. This is defined in the method [create_logger_for_connection](@ref sonicpackage.logging.create_logger_for_connection).

The device can also send logs and those logged via a device logger in the @ref sonicprotocol.SonicProtocol class.

SonicControl uses Log handlers to display then the logs in the **Logging Window**.

@}