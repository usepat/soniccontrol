## Settings page

The settings page is used for configuring a static state for a SonicDevice system. So for instance a concrete configuration of all atf's and atk's or the configuration of other values. These configurations (or states) are saved and stored locally, so that the user can change a configuration fast and not remember all the values. Naturally, the user can add, modify and delete configurations. Other functionalities that should be present in the settings page are "updating the firmware", and "SonicControl specific configurations (that do not exist up until now)".

### Requirements

- [ ] The user can set all ``atf's`` and ``atk's`` and ``att's``
- [ ] The user can manage many configurations
- [ ] The user can modify configurations
- [ ] The user can delete, and add configurations
- [ ] The user can activate a configuration and SonicControl sends this data to the SonicDevice
- [ ] The user can name a configuration
- [ ] It is possible to locate a flash file and validate it
- [ ] Before flashing, the system checks the flash file and looks for possible flaws
- [ ] After file-checkup but before the flashing, SonicControl tells the user the saftey rules while updating the firmware
- [ ] After the flashing process, SonicControl reconnects automatically and dumps a log-report of the process