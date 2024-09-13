*** Settings ***
Library    sonic_robot.RobotRemoteController    log_path=${OUTPUT_DIR}    AS    RemoteController
Variables    sonic_robot.variables

Suite Setup    Connect to device
Suite Teardown    RemoteController.Disconnect



*** Variables ***
${TARGET}             simulation        # can be either "simulation" or "url"
${SIMULATION_EXE_PATH}  ${None}
${URL}  ${None}



*** Test Cases ***

Set frequency updates device state
    ${frequency}=    RemoteController.Set "frequency" to "10000"
    Should Contain    ${frequency}    10000 Hz



*** Keywords ***

Connect to device
    IF    "${TARGET}" == 'simulation'
        IF  ${SIMULATION_EXE_PATH} is None
            Set Suite Variable    ${SIMULATION_EXE_PATH}    %{SIMULATION_EXE_PATH}    # robotcode: ignore
        END
        RemoteController.Connect via process to    ${SIMULATION_EXE_PATH}
    ELSE
        IF    "${URL}" == 'url'
            Fail    msg=No url to the serial port was provided
        END
        RemoteController.Connect via serial to    ${URL}
    END
       