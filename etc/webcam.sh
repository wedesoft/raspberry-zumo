#!/bin/sh
ffmpeg -s 640x480 -f video4linux2 -r 12 -i /dev/video0 -fflags nobuffer -rtsp_transport tcp http://localhost:8090/feed1.ffm
