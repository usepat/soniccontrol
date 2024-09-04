@defgroup SonicControlGui
@addtogroup SonicControlGui
@{

# Sonic Control GUI {#SonicControlGui}

## Brief Description

SonicControlGui is a GUI Application that uses internally [SonicPackage](#SonicPackage) to control ultra sonic devices from usePAT.

## Project Structure

The project has following directories:
- **bin**: contains binaries
  - **font_install**: Scripts to install fonts
- **resources**: Resources that get used by the application
  - **pictures**
  - **icons**
  - **fonts**
  - **texts**
- **state_fetching**: Those are helper classes that function as a glue between SonicPackage and SonicControl. Most of them are models for the [MVP architecture](#MVPPattern).
- **utils**: helper classes, miscellaneous code.
- **widgets**: Widgets that can be used and reused across the applications. Do not contain business logic. Mostly only for presentation.
- **views**: Windows, Tabs and Views. Do not get reused normally. And their presenters directly execute business logic in SonicPackage.
  - **core**: Views for managing devices.
  - **configuration**: Views and classes for configuring the device.
  - **control**: Views for controlling the device (and logging, because I did not know where to put it)
  - **measure**: Views for measuring.

## Handling Resources

To load resources correctly you should use [importlib.resources](). 
```python
from importlib import resources as rs

LOGGING_CONFIG = Path(str(rs.files(soniccontrol_gui).joinpath("log_config.json")))
```
This is necessary, because Python applications can also lie and be started from a zip. And for the application to find the resources correctly, this approach is needed.

Paths to the resources are defined in [constants](@ref soniccontrol_gui.constants) and [Resources](@ref soniccontrol_gui.resources._Resources) and [Images](@ref soniccontrol_gui.resources._Images)

@}