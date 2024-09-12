*** Settings ***
Library    sonic_robot.RobotSonicControlGui    AS    Gui
Variables    sonic_robot.variables

Suite Setup    Open device window
Suite Teardown    Gui.Close app



*** Variables ***
${TIMEOUT_CONNECTION_MS}    ${60000}
${TIMEOUT_MS}    ${2000}
${SIMULATION_EXE_PATH}    ${None}



*** Test Cases ***

Set frequency over home tab updates status bar
    ${frequency}    Set Variable    "200000"
    Gui.Set text of widget "${HOME_FREQUENCY_ENTRY}" to "${frequency}"
    Gui.Press button "${HOME_SEND_BUTTON}"
    ${frequency_gui}=     Gui.Wait up to "${TIMEOUT_MS}" ms for the widget "${STATUS_BAR_FREQ_LABEL}" to change text
    Should Contain    ${frequency_gui}    ${frequency}    # TODO: use a better check



*** Keywords ***

Open device window
    IF  ${SIMULATION_EXE_PATH} is None
        Set Suite Variable    ${SIMULATION_EXE_PATH}    %{SIMULATION_EXE_PATH}    # robotcode: ignore
    END
    Gui.Open app    ${SIMULATION_EXE_PATH}
    Gui.Press button "${CONNECTION_CONNECT_TO_SIMULATION_BUTTON}"
    Gui.Wait up to "${TIMEOUT_CONNECTION_MS}" ms for the widget "${HOME_DEVICE_TYPE_LABEL}" to be registered


