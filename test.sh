#!/usr/bin/env bash

for dir in Lulesh linux_perf analysis; do
  python3 $dir/_test.py
done
