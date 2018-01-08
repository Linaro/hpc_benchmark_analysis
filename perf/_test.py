#!/usr/bin/env python3

from perf import LinuxPerf

date = LinuxPerf(['date'])
date.stat()
date.parse()
