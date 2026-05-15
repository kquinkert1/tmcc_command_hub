#!/bin/bash
source ~/venv/bin/activate
export PYTHONPATH=~/BTTM/src/tmcc_command_hub

if [ "$1" == "--app" ]; then
    python3 ~/BTTM/src/tmcc_command_hub/tmcc/web/app.py
else
    python3 ~/BTTM/src/tmcc_command_hub/tmcc/web/app.py&
    sleep 5
    python3 ~/BTTM/src/tmcc_command_hub/tmcc/dispatchers/serial_dispatcher.py 
fi
