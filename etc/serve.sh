#!/bin/sh
ffmpeg -r 30 -i /dev/video0 -c:v libx265 -preset ultrafast -x265-params crf=23 -vf 'transpose=dir=clock,transpose=dir=clock' -strict experimental -f mpegts udp://wedemob:8000
