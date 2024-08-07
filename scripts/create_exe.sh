#!/bin/bash
WORKSPACE_DIR=$1

echo "create exe file with pyinstaller"

pyinstaller --noconfirm --onedir --windowed \
--name "SonicControl" \
--contents-directory "." \
# --add-data "${WORKSPACE_DIR}/resources:resources/" \
# --add-data "${WORKSPACE_DIR}/bin:bin/" \
# --add-data "${WORKSPACE_DIR}/configs:configs/" \
--collect-all soniccontrol \
"${WORKSPACE_DIR}/src/soniccontrol_gui/__main__.py"