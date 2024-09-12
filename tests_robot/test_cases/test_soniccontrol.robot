*** Settings ***
Library    sonic_robot.RobotSonicControlGui    AS    Gui
Variables    sonic_robot.variables

Suite Setup    Open device window
Suite Teardown    Gui.Close app



*** Variables ***
${TIMEOUT_CONNECTION_MS}    ${60000}
${TIMEOUT_MS}    ${10000}
${SIMULATION_EXE_PATH}    ${None}



*** Test Cases ***

Set gain over home tab updates status bar
    ${gain}    Set Variable    100
    Gui.Set text of widget "${HOME_GAIN_ENTRY}" to "${gain}"
    Gui.Press button "${HOME_SEND_BUTTON}"
    ${gain_gui}=     Gui.Wait up to "${TIMEOUT_MS}" ms for the widget "${STATUS_BAR_GAIN_LABEL}" to change text
    Should Contain    ${gain_gui}    ${gain}    # TODO: use a better check


*** Keywords ***

Open device window
    IF  ${SIMULATION_EXE_PATH} is None
        Set Suite Variable    ${SIMULATION_EXE_PATH}    %{SIMULATION_EXE_PATH}    # robotcode: ignore
    END
    Gui.Open app    ${SIMULATION_EXE_PATH}
    Gui.Press button "${CONNECTION_CONNECT_TO_SIMULATION_BUTTON}"
    Gui.Wait up to "${TIMEOUT_CONNECTION_MS}" ms for the widget "${HOME_DEVICE_TYPE_LABEL}" to be registered
    Gui.Let the app run free for "5" s    # Ensure that stuff is loaded and initialized correctly

