#!/bin/bash

PID=$(ps -ef | grep main.py | head -n1 | awk {'print $2'})
echo $(ps -ef | grep main.py | head -n1)
echo $PID
kill -9 $PID
echo "==kill check=="
echo $(ps -ef | grep main.py)
echo "==main Stop=="
echo "[$(date)] ==!main Stop!==" >>./nohup.out
