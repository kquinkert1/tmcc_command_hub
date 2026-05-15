#!/bin/bash
source ~/venv/bin/activate

python3 ~/BTTM/src/tmcc_command_hub/tmcc/dispatchers/serial_dispatcher.py &
DISPATCHER_PID=$!

python3 ~/BTTM/src/tmcc_command_hub/tmcc/web/app.py

kill $DISPATCHER_PID
