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
  * Filenames, separated by [sep] (see below), specify hierarchy
    - Example: gcc-ofast-a57-8 -> gcc -Ofast -mcpu=A57, 8 cores
    - Example: { gcc, llvm } - { O2, O3 } - [ elapsed, cache-misses, ... ]
  * Analysis in categories are specified by data_string
    - Example: -d sep=-,outlier=1,cluster=2,fit=3
  * If using multiple log dirs, naming convention needs to be the same

 Data String format (losely documented):
  * sep=c     : single char separator in logs.
                Ex: sep=- -> foo-bar-baz = ['foo', 'bar', 'baz']
  * none      : Do nothing (ignore that category)
  * outlier=N : warn if found outliers with threshold N (see outlier.py)
                If only two values, warn if difference > N
  * cluster=N : find N clusters in the data, warn if outliers
                Warning, this algorithm includes random guesses
  * fit=N     : try to fit a polynomial of power N (least squares)
"""

import importlib
import re

def load_analysis(plugin, data):
    """Loads module plugin.py"""
    keyval = plugin.split('=')
    if keyval[0] == "none":
        return None

    mod = importlib.import_module(keyval[0])
    if keyval[0] == "outlier":
        if len(keyval) < 2:
            raise ValueError("Outlier format is 'outlier=N'")
        return mod.Outliers(data, keyval[1])
    elif keyval[0] == "cluster":
        if len(keyval) < 2:
            raise ValueError("Cluster format is 'cluster=N'")
        return mod.Clustering(data, keyval[1])
    elif keyval[0] == "fit":
        if len(keyval) < 2:
            raise ValueError("Fit format is 'fit=N,K'")
        return mod.CurveFit(data, data, keyval[1]) # fixme
    else:
        raise ValueError("Invalid Analysis pass requested")

class Data:
    """Class that holds categories and log data in a hierarchical way"""
    def __init__(self, name, data_string):
        self.name = name
        self.analyses = list()
        self.logs = dict()
        self.sep = None
        self.num_cat = 0
        self.num_logs = 0
        self.parse_data_string(data_string)

    def parse_data_string(self, data_string):
        """Parses data string to know how to split logs and
           get statistical data from each category"""
        self.datastr = data_string
        if not self.datastr:
            return
        args = self.datastr.split(',')
        for arg in args:
            if not self.sep:
                keyval = arg.split("=")
                if keyval[0] != "sep":
                    raise ValueError("First data string key should be sep")
                if len(keyval) < 2:
                    raise ValueError("Sep format is 'sep=c'")
                self.sep = keyval[1]
            else:
                self.analyses.append(load_analysis(arg, []))


    def add_log(self, run, log, data):
        """Add a log file to a run"""

        # Validate input
        if not isinstance(run, str):
            raise TypeError("A run must be a str")
        if not isinstance(log, str):
            raise TypeError("A log must be a str")
        # Remove extension, split by separator
        cats = re.sub(r'\.[^-\.]+$', r'', log).split(self.sep)
        if not self.num_cat and len(cats) == 1:
            print("Warning: Mo separators in lognames. Using one category")
        if self.num_cat and len(cats) != self.num_cat:
            raise ValueError("Different number of separators in log file names")
        else:
            self.num_cat = len(cats)
        if self.analyses and len(cats) != len(self.analyses):
            raise ValueError("Different number of categories and analysis in -d argument")

        # Add runs / logs to the structure
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
        self.num_logs += 1

    def __str__(self):
        """Class name, for lists"""
        return "Data: " + self.name

    def __repr__(self):
        """Pretty-printing"""
        string = "[ Data (" + self.name + "): "
        string += repr(self.num_logs) + " log(s) in "
        string += repr(len(self.logs)) + " run(s), "
        string += repr(self.num_cat) + " categorie(s) ]"
        return string

    def summary(self):
        """ Print a summary of the data"""
        if self.analyses:
            print(" + Analyses:")
            for analysis in self.analyses:
                print(" - " + repr(analysis))
            print("")

        print(" + Logs:")
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
