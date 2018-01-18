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
    """Class that holds categories and log data in a hierarchical way"""
    def __init__(self, name):
        self.name = name
        self.logs = dict()
        self.categories = 0

    def add_log(self, run, log, data):
        """Add a log file to a run"""

        # Validate input
        if not isinstance(run, str):
            raise "A run must be a str"
        if not isinstance(log, str):
            raise "A log must be a str"
        cats = log.replace('.log', '').split('-')
        if not self.categories and len(cats) == 1:
            print("Warning: Mo '-' separators in lognames. Using one category")
        if self.categories and len(cats) != self.categories:
            raise "Different number of '-' separators in log file names"

        # Add runs / logs to the structure
        self.categories = len(cats)
        if run not in self.logs:
            self.logs[run] = dict()

        # For each category, build the tree
        data.set_name(log)
        pointer = self.logs[run] # (chuckle)
        last = cats[-1]
        for cat in cats:
            if cat == last:
                pointer[cat] = data
            else:
                if cat not in pointer:
                    pointer[cat] = dict()
                pointer = pointer[cat]

    def summary(self):
        """ Print a summary of the data"""
        for run in self.logs:
            for cat in self.logs[run]:
                _summary(self.logs[run][cat], "")

def _summary(data, padding):
    """Recurse through categories, dump last data"""
    # Dictionaries are categories
    if isinstance(data, dict):
        for cat, _ in data.items():
            print(padding + cat)
            _summary(data[cat], padding + "  ")

    # Data elements are leaf nodes
    else:
        print(padding + "Logfile: " + data.name)
        # Hardcode to get all keys for now
        for key, val in data.data.items():
            print(padding + key + " = " + val)
        for key, val in data.ext.items():
            print(padding + key + " = " + val)
        print('')
