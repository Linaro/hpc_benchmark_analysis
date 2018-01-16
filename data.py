"""
 Data - A class with all the information (and meta information) about a single
 benchmark, with multiple runs.

 Each run can mean different architectures, different compiler options, number
 of cores/threads, etc.

 This data strcture doesn't discern any of that, but there are a few assumptions
 that define the structure of the data.

 Assumptions:
  * All logs are results from the same benchmark in different modes
    - Example: different compiler options, number of cores, etc.
  * Filenames, separated by dashes, specify hierarchy
    - Example: benchmark-ofast-a57-8 -> <compiler> -Ofast -mcpu=A57, 8 cores
  * Leaf nodes represent data, branches are categories, root node is benchmark name
    - Example: { gcc, llvm } - { O2, O3 } - [ elapsed, cache-misses, ... ]
  * If using multiple log dirs, naming convention needs to be the same
"""

class Data:
    """Blerg"""
    def __init__(self, name):
        self.name = name
        self.logs = dict()

    def add_run(self, rundir):
        """Add a run to the data"""
        if not isinstance(rundir, str):
            raise "A run must be a name"
        self.logs[rundir] = list()

    def add_log(self, run, log, data):
        """Add a log file to a run"""
        if not isinstance(log, str):
            raise "A log must be a name"
        if not self.logs[run]:
            self.add_run(run)
        data.set_name(log)
        self.logs[run].append(data)

    def summary(self):
        """ Print a summary of the data"""
        for run in self.logs:
            for log in self.logs[run]:
                # Hardcode to get all keys for now
                for key, val in log.data.items():
                    print(key + " = " + val)
                for key, val in log.ext.items():
                    print(key + " = " + val)
