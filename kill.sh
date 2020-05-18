### This bash script should help you stop the communication stack.
### In order to make this script executable on your system, run:
###
###   chmod +x kill.sh
###

#!/bin/sh
# set -e

echo "Killing webots"
pkill webots

echo "Killing james"
pkill python3

echo "Killing controller"
pkill controller
