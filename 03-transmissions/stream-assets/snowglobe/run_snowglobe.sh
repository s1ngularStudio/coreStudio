#!/bin/bash
# Double-click won't work for a .sh on macOS by default -- run this from Terminal instead:
#   cd into this folder (stream-assets/snowglobe/), then: ./run_snowglobe.sh
#
# Opens the snowglobe window (1080x1920, chroma key green background). Capture it in OBS
# with a Window Capture source + Chroma Key filter. Idle until the chat bot's !snow command
# writes to snow_trigger.txt, then flakes fall for ~12s per trigger.
cd "$(dirname "$0")"
../../../.venv/bin/python snowglobe.py
