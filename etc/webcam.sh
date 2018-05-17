#!/bin/sh
ffserver -f /etc/ffserver.conf & ffmpeg -v verbose -r 5 -s 600x480 -f video4linux2 -i /dev/video0 -override_ffserver -c:v mjpeg -metadata:s:v rotate=0 -vf 'transpose=dir=clock,transpose=dir=clock' http://localhost:8090/feed1.ffm
