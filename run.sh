# This bash script should help you start the communication stack.
# In order to make this script executable on your system, run:
#
#   chmod +x run.sh
#



WEBOTS_HOME=/usr/local/webots
GIT_PATH=/home/fabian/uni/ees-pees

WORLD_FILE=/webots/worlds/prototypes.wbt


CONTROLLER=/controller/


webots ${GIT_PATH}${WORLD_FILE}
