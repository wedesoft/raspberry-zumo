#!/usr/bin/env python
import cv2
camera = cv2.VideoCapture(0)
status, img = camera.read()
cv2.imwrite("test.png", img)
