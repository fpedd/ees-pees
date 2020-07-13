### This bash script should help you stop the communication stack.

#!/bin/sh
# set -e

echo "Killing webots"
pkill -15 webots        # kill it nicely with SIGTERM
pkill -9 webots         # if webots is not nice, kill it hard with SIGKILL

echo "Killing backend"
pkill -15 python3       # kill it nicely with SIGTERM

echo "Killing controller"
pkill -15 controller    # kill it nicely with SIGTERM
