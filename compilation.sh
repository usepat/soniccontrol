#!/bin/bash

# SETUP
(
    rm -rfd venv
    python -m venv venv
    source ./venv/bin/activate
    pyhon -m pip install pyinstaller
    python -m pip install -e .
)

python -m PyInstaller --noconfirm --log-level=WARN \
    --noconsole \
    --collect-submodules=./src/soniccontrol \
    --icon=./src/soniccontrol/pictures/welle.ico \
    --name=SonicControl-1.9.3 \
    ./src/soniccontrol/__main__.py
