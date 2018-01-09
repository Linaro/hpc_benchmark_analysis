#!/usr/bin/env python3
"""Linux Tools' Perf wrapper"""

# Module: linux_perf
# Purpose: Core module, includes all others
#
# Usage:
#  app = LinuxPerf(['myapp', '-flag', 'etc'])
#  app.append_argument('-new_flag')
#  repeat = 5
#  events = ['cycles', 'cache-misses']
#  app.stat(repeat, events)
#  print app.cycles(),' +- ',app.cycles_stdev()
#  print app.cache_misses(),' +- ',app.cache_misses_stdev()
#
# Plugin: parses the output of a specific benchmark, returns a dictionary
# with data to be used for statistics later, will be combined with the perf
# data

import subprocess

class LinuxPerf:
    """Main class, calls perf stat with some options, saves output for plugins
       to analyse, parses and stores the perf data in the object for later
       enquiry.
    """
    def __init__(self, program=None, plugin=None):
        # list of arguments
        self.program = list()
        if isinstance(program, list):
            self.program.extend(program)
        # external plugin, benchmark specific
        self.plugin = plugin
        # list of events
        self.events = list()
        # gathered data by perf and benchmark plugin
        self.data = dict()
        # raw output / stderr (perfdata)
        self.output = None
        self.perfdata = None

    def append_argument(self, argument):
        """Appends argument(s) to the program list"""
        if isinstance(argument, list):
            self.program.extend(argument)
        else:
            self.program.append(argument)

    def stat(self, repeat=1, events=None):
        """Runs perf stat on the process, saving the output"""
        call = ['perf', 'stat']
        # Repeat the run N times, reports stdev
        if repeat > 1:
            call.extend(['-r', repeat])
        # Collects only a few events (empty = all)
        if isinstance(events, list):
            self.events.extend(events)
        if self.events:
            call.append('-e')
            ev_str = ''
            for e in self.events:
                ev_str += e
                ev_str += ','
            ev_str.pop()
            print(ev_str)
            call.append(ev_str)
        # Adding program to perf
        call.extend(self.program)
        # Call and collect output
        result = subprocess.run(call, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.output = result.stdout
        self.perfdata = result.stderr

    def parse(self):
        """Parses the output of perf stat"""
        # First, passes the output for the plugin to fill in its own data
        if self.plugin:
            results = self.plugin.parse(self.output)
            self.data += results
        # TODO: Parse perf output
        print(self.perfdata)
