#!/usr/bin/env bash

for dir in Lulesh linux_perf; do
  python3 $dir/_test.py
done
