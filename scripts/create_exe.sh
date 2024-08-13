#!/bin/bash
WORKSPACE_DIR=$1

echo "create exe file with pyinstaller"

pyinstaller --noconfirm --onedir --windowed \
--name "SonicControl" \
--collect-all soniccontrol_gui \
--collect-all sonicpackage \
--collect-all shared \
"${WORKSPACE_DIR}/src/soniccontrol_gui/__main__.py"