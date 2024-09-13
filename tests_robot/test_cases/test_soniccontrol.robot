*** Settings ***
Library    sonic_robot.RobotSonicControlGui    AS    Gui
Library    OperatingSystem

Variables    sonic_robot.variables

Suite Setup    Open device window
Suite Teardown    Gui.Close app

Keyword Tags    descaler    mvp_worker



*** Variables ***
${TARGET}    simulation    # can be either "simulation" or "url"
${SIMULATION_EXE_PATH}    ${None}
${URL}    ${None}

${TIMEOUT_CONNECTION_MS}    ${60000}
${TIMEOUT_MS}    ${10000}


*** Test Cases ***
Set frequency over home tab updates status bar
    [Tags]    -descaler
    Gui.Set text of widget "${HOME_FREQUENCY_ENTRY}" to "100000"
    Gui.Press button "${HOME_SEND_BUTTON}"
    ${freq_gui}=     Gui.Wait up to "${TIMEOUT_MS}" ms for the widget "${STATUS_BAR_FREQ_LABEL}" to change text
    Should Contain    ${freq_gui}    100    # TODO: use a better check



*** Keywords ***

# TODO: This has to be tested
Connect via url "${URL}"
    IF  ${URL} is None
        Fail    msg=No url was provieded
    END
    Gui.Set text of widget "${CONNECTION_PORTS_COMBOBOX}" to "${URL}"
    Gui.Press button "${CONNECTION_CONNECT_VIA_URL_BUTTON}"

Delete simulation memory file
    Remove File    ./fakeDataFram.bin


Open device window
    IF  ${SIMULATION_EXE_PATH} is None
        Set Suite Variable    ${SIMULATION_EXE_PATH}    %{SIMULATION_EXE_PATH}    # robotcode: ignore
    END
    Gui.Open app    ${SIMULATION_EXE_PATH}

    IF  "${TARGET}" == "simulation"
        Delete simulation memory file
        Gui.Press button "${CONNECTION_CONNECT_TO_SIMULATION_BUTTON}"
    ELSE IF    "${TARGET}" == "url"
        Connect via url "${URL}"
    ELSE
        Fail    msg=The target specified is not valid: ${TARGET}
    END

    Gui.Wait up to "${TIMEOUT_CONNECTION_MS}" ms for the widget "${HOME_DEVICE_TYPE_LABEL}" to be registered
    Gui.Let the app run free for "5" s    # Ensure that stuff is loaded and initialized correctly

