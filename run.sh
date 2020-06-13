#!/bin/bash

# 1. Run Redis server
nohup redis-server &

# 2. Run Flask server as a resource controller
# get controller name from argument. e. g. sh run.sh basic
python3 "$1"_controller.py