#!/usr/bin/env pypy3

# bu.py
# backup utility
#
# backs up all files within a list, creating directories as needed to maintain
# structure.
#
# BACKUP_DIR is not automatically created if it does not exist. user must create
# it manually or use the --create argument.

# author/license info
#

# TODO:
#   use alternative to sys.argv. popopt or w/e it was for optional parameters
#   docs for FILES structure for list
#   default to reading config from ~/.config/bupy/bupy.conf
#   --config filename.conf
#

# imports
import os
import shutil
import sys

# global vars
BASE_DIR = "/home/nvnehi/"
BACKUP_DIR = "/home/nvnehi/dotfiles/"
VERBOSE=False
FILES = [
    # ~/.config files
    ".config/i3/config",
    ".config/compton/compton.conf",
    ".config/dunst/dunstrc",
    ".config/mpd/mpd.conf",
    ".config/mpDris2/mpDris2.conf",
    ".config/mpv/mpv.conf",
    [
        ".config/pulse/",
        "client.conf",
        "daemon.conf",
        "default.pa",
        "system.pa",
    ],
    [
        ".config/ranger/",
        "rc.conf",
        "rifle.conf",
        "colorschemes/japanesque.py"
    ],
    # outside of ~/.config
    ".ncmpcpp/config",
    [
        ".Xresources.d/",
        "rofi",
        "urxvt",
        "xft"
    ],
    ".bashrc",
    ".Xresources",
    ".xinitrc",
    "bar.py",
    "lemonbar_status.py",
    "bu.py",
    [
        ".weechat/",
        "alias.conf",
        "buffers.conf",
        "charset.conf",
        "exec.conf",
        "irc.conf",
        "iset.conf",
        "logger.conf",
        "plugins.conf",
        "relay.conf",
        "script.conf",
        "sec.conf",
        "trigger.conf",
        "weechat.conf",
        "xfer.conf",
    ],
    "firefox_minimal.css",
    "reddit_clean_naut_bubblegum.css"
]

# functions
def backup(files, base_dir=""):
    for elem in files:
        if isinstance(elem, list):
            # recursively unwrap lists
            dir, *additional_files = elem
            backup(additional_files, os.path.join(base_dir, dir))
            continue

        file = os.path.join(base_dir, elem)
        if os.path.isfile(file):
            dst = os.path.join(BACKUP_DIR, file[len(BASE_DIR):])
            dir = os.path.dirname(dst)

            if not os.path.isdir(dir):
                os.makedirs(dir)

            if VERBOSE:
                print("{} -> {}".format(file, dir))

            shutil.copyfile(file, dst)
        else:
            print("warning: Ignoring \"{}\" as it does not exist".format(file))

def restore():
    global BACKUP_DIR, BASE_DIR

    # swap base/backup directories and the backup method works in reverse
    BACKUP_DIR, BASE_DIR = BASE_DIR, BACKUP_DIR

    if VERBOSE:
        print("restoring files to {}".format(BACKUP_DIR))

def create():
    if VERBOSE:
        print("creating {}".format(BACKUP_DIR))

    if os.path.isdir(BACKUP_DIR):
        print("warning: {} already exists".format(BACKUP_DIR))
    else:
        os.makedirs(BACKUP_DIR)


def clean():
    if VERBOSE:
        print("removing {}".format(BACKUP_DIR))

    if os.path.isdir(BACKUP_DIR):
        shutil.rmtree(BACKUP_DIR)
    else:
        print("error: {} does not exist".format(BACKUP_DIR))

def help():
    print("(simple) backup utility")
    print()
    print("copies all files in the FILES list(within python file) to BACKUP_DIR, maintaining directory structure")
    print()
    print("-h | --help")
    print("\tthis screen")
    print("-v | --verbose")
    print("\tenables verbosity")
    print("-c | --clean")
    print("\tremoves the backup directory(including files within it)")
    print("--create")
    print("\tcreates the backup directory to use")

# entry point
def main():
    for arg in sys.argv:
        if arg == "-h" or arg =="--help":
            help()
            return True

        if arg == "-v" or arg == "--verbose":
            global VERBOSE
            VERBOSE = True

        if arg == "-c" or arg == "--clean":
            clean()
            return True

        if arg == "--create":

            create()
        if arg == "-r" or arg == "--restore":
            restore()

    if os.path.isdir(BACKUP_DIR):
        if os.access(BACKUP_DIR, os.W_OK):
            backup(FILES, BASE_DIR)
        else:
            print("error: no write access to {}".format(BACKUP_DIR))
    else:
        print("error: {} does not exist. Please create it.".format(BACKUP_DIR))

    sys.exit(0)

# begin
main()
