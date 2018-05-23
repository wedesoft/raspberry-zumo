#!/bin/sh
ffplay -fs -vf transpose=dir=clock,transpose=dir=clock http://raspberrypi:8090/test.mjpg
