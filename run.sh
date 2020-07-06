### This bash script should help you start the communication stack.

#!/bin/sh
set -e

### Path to External Controller
EXT_CTRL=/controller

### Path to Webots World and Internal Controller
WORLD_FILE=/webots/worlds/test_run.wbt
INT_CTRL=/webots/controllers/internal

### Path to Backend Script
# BCKND_SCRIPT=/backend/james.py    # <- continous action example
BCKND_SCRIPT=/backend/timmy.py    # <- discrete action example
# BCKND_SCRIPT=/backend/schnitty.py    # <- continous and discrete action example
                                       # (use space to switch between modes)
# BCKND_SCRIPT=/backend/tommy.py      # <- mixed action example


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

echo "Clean and compile the Internal Controller"
make clean -C .${INT_CTRL}
make all -C .${INT_CTRL}

echo "Start the External Controller"
${TERM_EM} .${EXT_CTRL}/build/controller ${DETACH}

echo "Start Webots and the Internal Controller"
${TERM_EM} webots .${WORLD_FILE} ${DETACH}

echo "Start the Backend"
${TERM_EM} python3 .${BCKND_SCRIPT} ${DETACH}
