@defgroup SystemTests
@ingroup ProjectSetup
@addtogroup SystemTests
@{

# System Testing {#SystemTests}

In contrast to [Unit testing](@ref UnitTests), System testing is about testing the whole system and not just a single unit of it.
There is also integration testing, that focus on testing if a collection of units works together as expected. The transition from integration testing to system testing is fluid.

For the system testing we use a binary of our [firmware](https://github.com/usepat/sonic-firmware/tree/stable) that simulates it locally on the pc (but only for Linux). 
We can start this binary as a process in the command line and can communicate with it over `stdout` and `stdin`.
In the code we do this over [CLIConnectionFactory](@ref soniccontrol.ConnectionFactory.CLIConnectionFactory).

For writing the system tests we use the robot framework.

## Robot Framework

The [Robot Framework](https://robotframework.org/robotframework/latest/RobotFrameworkUserGuide.html) is a popular testing framework for system tests. 
You can install robot framework via `pip install robot-framework`.
You can write Python libraries for it as API and then use them together with thousand others libraries, provided by the robot community.
The *src/sonic_robot* folder contains the robot library for testing the application code.
In the *tests_robots/test_cases* folder are the tests.
Here is an example for a robot file
```robot
*** Settings ***
Library    calculator.py
Suite Setup    Log    Starting Calculator Tests
Suite Teardown    Log    Calculator Tests Finished

*** Variables ***
${A}    10
${B}    5
${ZERO}    0

*** Test Cases ***

Addition Test
    [Documentation]    Verify that the addition function returns the correct sum.
    ${result}=    Add    ${A}    ${B}
    Should Be Equal    ${result}    15

Division Test
    [Documentation]    Verify that the division function returns the correct quotient.
    ${result}=    Divide    ${A}    ${B}
    Should Be Equal    ${result}    2

Division By Zero Test
    [Documentation]    Verify that dividing by zero raises an exception.
    Run Keyword And Expect Error    ValueError    Divide    ${A}    ${ZERO}
```
The framework creates you reports in html and logs for your tests.
They can be found in *tests_robots/results*.
The path is specified via *.vscode/settings.json*:
```json
"robotcode.robot.outputDir": "${workspaceFolder}/tests_robot/results"
```

To run robot you can us the vscode *Test Tab* or run them directly via `robot .` in the command line.

For continuous integration with robot see this [page](@ref CIandCD)

@}