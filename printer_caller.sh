#!/bin/bash
# Activate virtual environment
source /home/pi/Projekte/Abfahrtsmonitor_NAHSH/venv311/bin/activate

# Infinite loop: run script every minute at 15 seconds past
while true; do
    now=$(date +%S)
    # wait until 1 seconds past
    sleep $(( (1 - 10#$now + 60) % 60 ))
    # run the script
    # python /home/pi/Projekte/Abfahrtsmonitor_NAHSH/print_screen_weather_busses.py
    python /home/pi/Projekte/Abfahrtsmonitor_NAHSH/print_screen_gravel.py
done
