#!/bin/sh
while true; do
  clear;
  py.test;
  inotifywait -e CLOSE_WRITE `git ls-files .`;
done
