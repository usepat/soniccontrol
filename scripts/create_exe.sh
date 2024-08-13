#!/bin/bash
WORKSPACE_DIR=$1

echo "create exe file with pyinstaller"

pyinstaller --noconfirm --onedir --windowed \
--name "SonicControl" \
--contents-directory "." \
--collect-all soniccontrol \
"${WORKSPACE_DIR}/src/soniccontrol_gui/__main__.py"