#!/usr/bin/env bash
export PYTHONPATH=$PYTHONPATH:/home/ubuntu/New_web
for process in `ps -ef |grep core.py |grep -v grep |awk '{print $2}'`
do
(kill -9 $process)
echo "kill "$process
done