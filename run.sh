#!/bin/bash

# 1. Run Redis server
nohup redis-server &

# 2. Run Flask along with Gunicorn as a resource controller
# get controller name from argument. e. g. sh run.sh basic
# may change the number of workers and the number of threads for each worker
gunicorn "$1":app -w 4 -b 0.0.0.0:8000