#!/bin/bash

# ref script
# https://velog.io/@johoon815/%EB%B9%84%ED%8A%B8%EC%BD%94%EC%9D%B8-%EC%9E%90%EB%8F%99%EB%A7%A4%EB%A7%A4-Ch.4-%EC%97%AC%EA%B8%B0%EC%84%9C-%EC%99%84%EC%84%B1
CURRENT=${PWD}
echo $CURRENT
. /home/ubuntu/yprite-workspace/dca-bot/.venv/bin/activate
echo "actiavte"
python3 -u /home/ubuntu/yprite-workspace/dca-bot/main.py 2>&1 |tee /home/ubunut/yprite-workspace/dca-bot/logfile.txt
