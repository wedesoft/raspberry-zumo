#!/bin/sh
ffplay -fs -vf transpose=dir=clock,transpose=dir=clock rtsp://raspberrypi:5554/test.mpeg4
