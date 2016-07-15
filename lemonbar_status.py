#!/usr/bin/env pypy3
#

# REQUIRES:
#   python libraries
#     i3ipc
#     python-mpd2
#   xdotool
#   amixer
#   mpc
#


# author info/license
#

# TODO:
#   maybe add named parameters for "".format() to reduce some clutter/additional typing
#   add statuses for:
#     mail
#     irc
#     battery
#     brightness
#   convert all the shell->mpc results to using the mpd library
#

# INFO:
#

# imports
import i3ipc
import re
import subprocess
import time
from mpd import MPDClient

# configuration
SECONDS_TO_SLEEP = 1
USE_I3 = True # if true, i3 workspaces are listed
USE_MPD = False # if true, media controls are enabled
MPD_SERVER = "localhost"
MPD_SERVER_PORT = 6600
ALSA_CHANNEL = "Master"
GAP_WIDTH = 30 # gap which is present at left/right of bar in pixels
DISK = "/dev/sdb3" # disk to check for space remaining
NETWORK_ADAPTER = "enp4s0" # network adapter to check for network status

# what is to be displayed
DISPLAY_WINDOW_TITLE = True
DISPLAY_SONG_INFO = True
DISPLAY_CLOUD_STATUS = False
DISPLAY_DISK_REMAINING = False
DISPLAY_NETWORK_STATUS = False
DISPLAY_VOLUME = True
DISPLAY_DATE = True
DISPLAY_TIME = True
DISPLAY_POWER = True
DISPLAY_NOTIFICATIONS = True

# global variables
if USE_I3:
  global I3_CONNECTION
  I3_CONNECTION = i3ipc.Connection()

if USE_MPD:
  global MPD_CLIENT
  MPD_CLIENT = MPDClient()
  MPD_CLIENT.connect(MPD_SERVER, MPD_SERVER_PORT)

# colors, in hex
COLOR_ACCENT    = "#bf5b75"
COLOR_NORMAL    = "#cccccc"
COLOR_HIGHLIGHT = "#ffffff"
COLOR_DARK      = "#777777"
COLOR_ICON      = "#777777"
COLOR_FAIL      = "#bf5b75"

# icons (defaults: font awesome)
ICON_WORKSPACES               = "\uf24d"
ICON_WINDOW                   = "\uf120"
ICON_SONG                     = "\uf025"
ICON_MEDIA                    = "\uf001"
ICON_MEDIA_CONTROLS_PREVIOUS  = "\uf049"
ICON_MEDIA_CONTROLS_BACK      = "\uf04a"
ICON_MEDIA_CONTROLS_STOP      = "\uf04d"
ICON_MEDIA_CONTROLS_PLAY      = "\uf04b"
ICON_MEDIA_CONTROLS_PAUSE     = "\uf04c"
ICON_MEDIA_CONTROLS_FORWARD   = "\uf04e"
ICON_MEDIA_CONTROLS_NEXT      = "\uf050"
ICON_CLOUD                    = "\uf16b"
ICON_CLOUD_SYNCED             = "\uf00c"
ICON_CLOUD_SYNCING            = "\uf021"
ICON_CLOUD_FAIL               = "\uf00d"
ICON_DISK                     = "\uf0a0"
ICON_NETWORK                  = "\uf201"
ICON_VOLUME                   = "\uf028"
ICON_VOLUME_MUTED             = "\uf026"
ICON_VOLUME_UNMUTED           = "\uf028"
ICON_DATE                     = "\uf133"
ICON_TIME                     = "\uf017"
ICON_POWER                    = "\uf011"
ICON_NOTIFICATIONS            = "\uf0c9"

# utility functions
# shamelessly taken from stackoverflow user: Mark Byers
def natural_sort(l):
    convert = lambda text: int(text) if text.isdigit() else text.lower()
    alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ]

    return sorted(l, key = alphanum_key)

def result_from_shell(cmd):
  return (
    subprocess
      .Popen(
        cmd,
        stdout = subprocess.PIPE,
        stderr = subprocess.PIPE,
        shell = True
      )
      .communicate()[0] # communicate() returns (stdout, stderr)
      .decode("utf-8")  # decode the bytes to utf-8
      .strip()          # strip the newline
  )

def get_workspaces():
  # stores the name of the focused workspace
  focused_workspace = ""
  # get a list of workspace related objects
  workspaces = I3_CONNECTION.get_workspaces()
  # stores the names of each workspace
  workspace_names = []

  # iterate the workspaces and save their names to workspace_names
  for workspace in workspaces:
    workspace_names.append(workspace.name)
    if workspace.focused:
      focused_workspace = workspace.name

  # build the string to return
  s = "%{{F{}}}{} %{{F-}}".format(COLOR_DARK, ICON_WORKSPACES)

  # iterate the workspace names and build the string to return to lemonbar
  for workspace_name in ( natural_sort(workspace_names)):
    # if the workspace is the focused workspace, highlight it to represent the fact
    if workspace_name == focused_workspace:
      s += "%{{+u}}%{{U{}}}%{{F{}}} ".format(COLOR_ACCENT, COLOR_HIGHLIGHT) + workspace_name + " %{F-}%{U-}%{-u} "
    else:
      s += "%{{F{}}} ".format(COLOR_NORMAL) + workspace_name + " %{F-} "

  return s

# returns true if there is a focused window
def is_window_focused():
  return True if len(result_from_shell("xdotool getactivewindow getwindowname")) > 0 else False

# returns the name of the focused window
def get_window_name():
  if is_window_focused():
    return (
      "%{{F{}}}{}%{{F-}} %{{F{}}}{}%{{F-}}"
      .format(
        COLOR_ICON,
        ICON_WINDOW,
        COLOR_NORMAL,
        result_from_shell("xdotool getactivewindow getwindowname")
      )
    )

  return ""

# returns if a song is playing
def is_song_playing():
  return result_from_shell("mpc status | tail -n 2 | head -n 1 | awk '{print $1;}' | tr -cd 'a-zA-Z'") == "playing"

# returns if the currently queued song is stopped
def is_song_stopped():
  return True if result_from_shell("mpc current") == "" else False

# returns the song time, or False if there is no song in queue
def get_song_time():
  if not is_song_stopped():
    return result_from_shell("mpc status | head -n 2 | tail -n 1 | awk '{{print $3}}'")

  return False

# returns the formatted song string, or "" if there is no song playing
def get_song():
  if not is_song_stopped():
    return (
      "%{{F{}}}{}%{{F-}} %{{F{}}}{}%{{F-}} %{{F{}}}[{}]{}{}%{{F-}}"
      .format(
        COLOR_ICON,
        ICON_SONG,
        COLOR_NORMAL,
        result_from_shell("mpc current"),
        COLOR_DARK,
        get_song_time(),
        " (paused)" if not is_song_playing() else "",
        " (muted)" if is_muted() else ""
      )
    )

  return ""

# returns the formatted media controls string
def get_media_controls():
  return (
    "%{{F{}}}{}%{{F-}} %{{F{}}}%{{A:mpc prev:}}{}%{{A}} %{{A:mpc seek -5:}}{}%{{A}} %{{A:mpc stop:}}{}%{{A}}%{{A:mpc toggle:}}{}%{{A}} %{{A:mpc seek +5:}}{}%{{A}} %{{A:mpc next:}}{}%{{A}}%{{F-}} "
    .format(
      COLOR_ICON,
      ICON_MEDIA,
      COLOR_NORMAL,
      ICON_MEDIA_CONTROLS_PREVIOUS,
      ICON_MEDIA_CONTROLS_BACK,
      ICON_MEDIA_CONTROLS_STOP + " " if not is_song_stopped() else "",
      ICON_MEDIA_CONTROLS_PAUSE if is_song_playing() else ICON_MEDIA_CONTROLS_PLAY,
      ICON_MEDIA_CONTROLS_FORWARD,
      ICON_MEDIA_CONTROLS_NEXT
    )
  )

# returns the formatted cloud storage status string
def get_cloud_storage_status():
  status = result_from_shell("dropbox-cli status")

  # display the icon that best corresponds with the status of the cloud storage daemon
  if "Indexing" in status or "Syncing" in status:
    ICON_STATUS = ICON_CLOUD_SYNCING
  elif "Up to date" in status or "Starting" in status:
    ICON_STATUS = ICON_CLOUD_SYNCED
  else:
    ICON_STATUS = ICON_CLOUD_FAIL

  return (
    "%{{F{}}}{}%{{F-}} %{{F{}}}{}%{{F-}} "
    .format(
      COLOR_ICON,
      ICON_CLOUD,
      COLOR_FAIL if ICON_STATUS == ICON_CLOUD_FAIL else COLOR_NORMAL,
      ICON_STATUS
    )
  )

# returns the formatted disk space that is remaining string
def get_disk_remaining():
  return (
    "%{{F{}}}{}%{{F-}} %{{F{}}}{}g%{{F-}} "
    .format(
      COLOR_ICON,
      ICON_DISK,
      COLOR_NORMAL,
      result_from_shell("df -H | grep " + DISK + " | awk '{print $4}' | tr -cd '0-9'")
    )
  )

# returns the formatted network status string
def get_network_status():
  return (
    "%{{F{}}}{}%{{F-}} %{{F{}}}{}%{{F-}} "
    .format(
      COLOR_ICON,
      ICON_NETWORK,
      COLOR_NORMAL,
      result_from_shell("cat /sys/class/net/" + NETWORK_ADAPTER + "/operstate")
    )
  )

# returns True if the alsa device is muted
def is_muted():
  status = result_from_shell("amixer get {} | awk '/Front Left:/ {{print $6}}'".format(ALSA_CHANNEL))

  if status == "[off]":
    return True

  return False

# returns the volume percentage
def get_volume_percentage():
  return result_from_shell("amixer get {} | awk '/Front Left:/ {{print $5}}' | tr -dc '0-9'".format(ALSA_CHANNEL))

# returns the formatted volume icon and percentage string
def get_volume():
  # set the volume icon depending if volume is muted or unmuted
  if is_muted():
    ICON_VOLUME = ICON_VOLUME_MUTED
  else:
    ICON_VOLUME = ICON_VOLUME_UNMUTED

  return (
    "%{{F{}}}%{{A3:amixer sset {} toggle:}}%{{A4:amixer sset {} 5%+:}}%{{A5:amixer sset {} 5%-:}}{}%{{F-}} %{{F{}}}{}%%{{F-}}%{{A}}%{{A}}%{{A}} "
    .format(
      COLOR_ICON,
      ALSA_CHANNEL,
      ALSA_CHANNEL,
      ALSA_CHANNEL,
      ICON_VOLUME,
      COLOR_FAIL if is_muted() else COLOR_NORMAL,
      get_volume_percentage()
    )
  )

# returns the formatted date string
def get_date():
  month = time.strftime("%m")
  day = time.strftime("%d")
  year = time.strftime("%y")

  return (
    "%{{F{}}}{}%{{F-}} %{{F{}}}{}%{{F-}}%{{F{}}}/%{{F-}}%{{F{}}}{}%{{F-}}%{{F{}}}/%{{F-}}%{{F{}}}{}%{{F-}} "
    .format(
      COLOR_ICON,
      ICON_DATE,
      COLOR_NORMAL,
      month,
      COLOR_DARK,
      COLOR_HIGHLIGHT,
      day,
      COLOR_DARK,
      COLOR_NORMAL,
      year
    )
  )

# returns the formatted time string
def get_time():
  hour = time.strftime("%I")
  minute = time.strftime("%M")

  return (
    "%{{F{}}}{}%{{F-}} %{{F{}}}{}%{{F-}}%{{F{}}}:%{{F-}}%{{F{}}}{}%{{F-}} "
    .format(
      COLOR_ICON,
      ICON_TIME,
      COLOR_NORMAL,
      hour,
      COLOR_DARK,
      COLOR_HIGHLIGHT,
      minute
    )
  )

# returns the formatted power string
def get_power():
  return (
    "%{{F{}}}{}%{{F-}} "
    .format(
      COLOR_ICON,
      ICON_POWER
    )
  )

# returns the formatted notifications string
def get_notifications():
  return (
    "%{{F{}}}%{{A:xdotool key Control+grave:}}%{{A3:xdotool key Control+Escape:}}{}%{{A}}%{{A}}%{{F-}} "
    .format(
      COLOR_ICON,
      ICON_NOTIFICATIONS
    )
  )

# builds the status string and returns it
def get_status():
  return (
    "%{{l}}%{{O{}}}{} {}%{{c}}  {}%{{r}}  {}{}{}{}{}{}{}{}{}%{{O{}}}"
    .format(
      GAP_WIDTH,
      get_workspaces() if USE_I3 else "",
      get_window_name() if DISPLAY_WINDOW_TITLE else "",
      get_song() if DISPLAY_SONG_INFO else "",
      get_media_controls() if USE_MPD and len(MPD_CLIENT.playlist()) > 0 else "",
      get_cloud_storage_status() if DISPLAY_CLOUD_STATUS else "",
      get_disk_remaining() if DISPLAY_DISK_REMAINING else "",
      get_network_status() if DISPLAY_NETWORK_STATUS else "",
      get_volume() if DISPLAY_VOLUME else "",
      get_date() if DISPLAY_DATE else "",
      get_time() if DISPLAY_TIME else "",
      get_power() if DISPLAY_POWER else "",
      get_notifications() if DISPLAY_NOTIFICATIONS else "",
      GAP_WIDTH
    )
  )

# entry point
def main():
  # print the status and sleep until interrupted
  while True:
    print(get_status())
    time.sleep(SECONDS_TO_SLEEP)

# begin
main()
