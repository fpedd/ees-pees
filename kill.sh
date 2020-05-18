### This bash script should help you stop the communication stack.

#!/bin/sh
# set -e

echo "Killing webots"
pkill webots

echo "Killing james"
pkill python3

echo "Killing controller"
pkill controller
