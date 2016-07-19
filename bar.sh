#!/bin/sh
#

# author info/license
#

# REQUIRES:
#   pypy3
#   lemonbar
#   fonts
#     dejavu sans mono
#     font awesome
#

# TODO:
#

# configuration
NAME="bar1"
GEOMETERY="1920x30"
UNDERLINE_PIXELS="3"
COLOR_BACKGROUND="#aa111111"
COLOR_FOREGROUND="#ffaaaaaa"
FONT1="DejaVu Sans Mono-10:Bold"
FONT2="FontAwesome-12"
ACTIONS="11"

# pipe status string to lemonbar, and pipe commands from it to the shell
pypy3 -u ~/lemonbar_status.py | lemonbar \
-p \
-n \
"$NAME" \
-g "$GEOMETERY" \
-B "$COLOR_BACKGROUND" \
-F "$COLOR_FOREGROUND" \
-a "$ACTIONS" \
-u "$UNDERLINE_PIXELS" \
-f "$FONT1" \
-f "$FONT2" | sh
