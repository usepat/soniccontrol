#!/bin/bash

WORKSPACE_DIR=$1

pyinstaller --noconfirm --onedir --windowed \
--name "SonicControl" \
--contents-directory "." \
--add-data "${WORKSPACE_DIR}/resources:resources/" \
--add-data "${WORKSPACE_DIR}/bin:bin/" \
--add-data "${WORKSPACE_DIR}/logs:logs/" \
"${WORKSPACE_DIR}/soniccontrol/__main__.py"