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
    - Example: -d sep=-,outlier=1/ac,cluster=2/ac,fit=3/al
  * If using multiple log dirs, naming convention (sep,cats) needs to be the same
  * Analysis "across" search for same category on other parent categories
  * Analysis "along" search for all categories on the parent categories

 Data String format (losely documented):
  * sep=c     : single char separator in logs.
                Ex: sep=- -> foo-bar-baz = ['foo', 'bar', 'baz']
  * none      : Do nothing (ignore that category)
  * outlier=N : warn if found outliers with threshold N (see outlier.py)
                If only two values, warn if difference > N
  * cluster=N : find N clusters in the data, warn if outliers
                Warning, this algorithm includes random guesses
  * fit=N     : try to fit a polynomial of power N (least squares)
  * ac/al     : across / along category analysis (default = across)
"""

import importlib
import re
from enum import Enum

def load_analysis(plugin, data):
    """Loads module plugin.py"""

    if plugin.startswith('none'):
        return None
    if not isinstance(data, list):
        raise TypeError("Data must be a list")

    # split string into three parts: key=value/type
    analysis_type = AnalysisType.across
    split = re.match(r'([^=]+)=([^/]+)/?(.*)', plugin)
    if not split:
        raise ValueError("Invalid plugin format")
    key = split.group(1)
    if not split.group(2):
        raise ValueError("Plugin must have at least one parameter")
    value = split.group(2)
    if split.group(3):
        if split.group(3) == 'al':
            analysis_type = AnalysisType.along
        elif split.group(3) != 'ac':
            raise ValueError("Invalid analysis type (must be ac/al)")

    mod = importlib.import_module(key)
    if key == "outlier":
        return Analysis(analysis_type, mod.Outliers(data, value))
    elif key == "cluster":
        return Analysis(analysis_type, mod.Clustering(data, value))
    elif key == "fit":
        return Analysis(analysis_type, mod.CurveFit(data, data, value)) # fixme
    else:
        raise ValueError("Invalid Analysis pass requested")

class AnalysisType(Enum):
    """Analysis Type"""
    across = 1
    along = 2

class Analysis:
    """Simple container for analysis info to help with analysing the data"""
    def __init__(self, analysis_type, plugin):
        self.type = analysis_type
        self.plugin = plugin
        self.validate()

    def validate(self):
        """Validates the data"""
        if not isinstance(self.type, AnalysisType):
            raise TypeError("Analysis type must be enum(ac/al)")

    def run(self, data):
        """Runs the analysis on the data"""
        return self.plugin(data)

    def __str__(self):
        """Class name, for lists"""
        return "Analysis: " + str(self.type) + ' ' + str(self.plugin)

    def __repr__(self):
        """Pretty-printing"""
        string = "[ Analysis (" + repr(self.type) + "), "
        if self.plugin:
            string += str(self.plugin) + " ]"
        return string

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
