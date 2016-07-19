#!/usr/bin/env pypy3
#

# author info/license
#

# TODO:
#

# imports
import subprocess

# configuration
NAME="bar"
WIDTH=1890
HEIGHT=30
MONITOR_WIDTH=1920
UNDERLINE_PIXELS=3
COLOR_BACKGROUND="#dd111111"
COLOR_FOREGROUND="#ffaaaaaa"
FONT1="DejaVu Sans Mono-10:Bold"
FONT2="FontAwesome-12"
ACTIONS=20
MONITORS=2

# entry points
def main():
  for i in range(MONITORS):
    x = i * MONITOR_WIDTH
    geometery = "{}x{}+{}".format(WIDTH, HEIGHT, x)
    # create the cmd to execute
    cmd = "pypy3 -u ~/lemonbar_status.py | lemonbar -p -n \"{}\" -g \"{}\" -B \"{}\" -F \"{}\" -a {} -u {} -f \"{}\" -f \"{}\" | sh".format(
      NAME,
      geometery,
      COLOR_BACKGROUND,
      COLOR_FOREGROUND,
      ACTIONS,
      UNDERLINE_PIXELS,
      FONT1,
      FONT2
    )

    # open the subprocess
    subprocess.Popen(cmd, shell=True)

# begin
main()
