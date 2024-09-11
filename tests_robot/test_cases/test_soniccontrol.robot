*** Settings ***
Library    sonic_robot.RobotSonicControlGui    AS    Gui
Variables    sonic_robot.variables

Suite Setup    Open device window
Suite Teardown    Gui.Close app



*** Variables ***
${TIMEOUT_CONNECTION_MS}    ${60000}
${TIMEOUT_MS}    ${2000}



*** Test Cases ***

Set frequency over home tab updates status bar
    ${frequency}    Set Variable    ${200000}
    Gui.Set text of widget "${HOME_FREQUENCY_ENTRY}" to "${frequency}"
    Gui.Wait up to "${TIMEOUT_MS}" ms for the widget "${STATUS_BAR_FREQ_LABEL}" to change
    ${frequency_gui}=    Gui.Get text of widget "${STATUS_BAR_FREQ_LABEL}"
    Should Contain    ${frequency_gui}    ${frequency}    # TODO: use a better check



*** Keywords ***

Open device window
    Gui.Open app
    Gui.Press button "${CONNECTION_CONNECT_TO_SIMULATION_BUTTON}"
    Gui.Wait up to "${TIMEOUT_CONNECTION_MS}" ms for the widget "${HOME_DEVICE_TYPE_LABEL}" to be registered


