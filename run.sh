### This bash script should help you start the communication stack.
### In order to make this script executable on your system, run:
###
###   chmod +x run.sh
###

#!/bin/sh
set -e

### Path to External Controller
EXT_CTRL=/controller

### Path to your local Webots installation
export WEBOTS_HOME=/usr/local/webots

### Path to Webots World and Internal Controller
WORLD_FILE=/webots/worlds/prototypes.wbt
INT_CTRL=/webots/controllers/internal_ctrl

### Path to Backend Script
BCKND_SCRIPT=/backend/james.py

### Terminal Emulator you want to use
TERM_EM=gnome-terminal\ -x
# TERM_EM=xterm\ -e

### Uncomment this if you want to run the processes detached
# DETACH=&

### This should point to where this bash script is at
# GIT_PATH="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

echo "Clean and compile the External Controller"
make clean -C .${EXT_CTRL}
make all -C .${EXT_CTRL}

echo "Clean and compile the Interal Controller"
make clean -C .${INT_CTRL}
make all -C .${INT_CTRL}

echo "Start the External Controller"
${TERM_EM} .${EXT_CTRL}/build/controller ${DETACH}

echo "Start Webots and the Internal Controller"
${TERM_EM} webots .${WORLD_FILE} ${DETACH}

echo "Start the Backend"
${TERM_EM} python3 .${BCKND_SCRIPT} ${DETACH}
