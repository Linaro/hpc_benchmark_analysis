"""
 Lulesh output parser
 Purpose: Parses Lulesh output, provide a dictionary, plugin for linux_perf

 Usage:
  lul = LuleshPerf()
  app = LinuxPerf(['lulesh2.0', '-flag', 'etc'], lul)
  app.stat()
  print app.cycles()
"""

import re

class LinuxPerfPlugin:
    """Plugin for LinuxPerf, parses Lulesh output, return dictionary"""
    def __init__(self):
        # Hard-coded list of perf events plus other data it spews
        # well, the ones we support at least
        self.fields = {
            'ProblemSize' : r'Problem size\s+=\s+(\d+)',
            'IterationCount' : r'Iteration count\s+=\s+(\d+)',
            'FinalEnergy' : r'Final Origin Energy\s+=\s+(\d+[^\s]*)',
            'MaxAbsDiff' : r'MaxAbsDiff\s+=\s+(\d+[^\s]*)',
            'TotalAbsDiff' : r'TotalAbsDiff\s+=\s+(\d+[^\s]*)',
            'MaxRelDiff' : r'MaxRelDiff\s+=\s+(\d+[^\s]*)',
            'Elements' : r'Total number of elements:\s+(\d+)',
            'Threads' : r'Num threads: (\d+)',
            'Grind' : r'Grind time\(us\/z\/c\)\s+=\s+(\d+)',
            'FOM' : r'FOM\s+=\s+(\d+)'
        }
        self.data = dict()
        self.raw = None

    def parse(self, results):
        """Parses raw output"""
        if isinstance(results, str):
            self.raw = results
        else:
            return None
        for field, regex in self.fields.items():
            match = re.search(regex, self.raw)
            if match:
                self.data[field] = match.group(1)
        return self.data

    def get_value(self, key):
        """ Get the value of an event or data"""
        if self.data and key in self.data:
            return self.data[key]
        return ''

    def __str__(self):
        """Class name, for lists"""
        return "LuleshPerfPlugin"

    def __repr__(self):
        """Pretty-printing"""
        string = "[ Lulesh: " + repr(len(self.fields)) + " field(s), "
        string += repr(len(self.data)) + " data points ]"
        return string
