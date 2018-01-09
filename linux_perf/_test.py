#!/usr/bin/env python3

from linux_perf import LinuxPerf

date = LinuxPerf(['date'])
date.stat()
date.parse()
