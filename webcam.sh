#!/bin/sh
ffmpeg -s 640x480 -f video4linux2 -r 5 -i /dev/video0 -vsync cfr http://localhost:8090/feed1.ffm
