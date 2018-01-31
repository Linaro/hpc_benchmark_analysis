"""
 AnalysisBase class, from which every analysis pass must inherit from.

 This class defines the base of each analysis pass, and force them to conform to
 a known standard, so that scripts that load the modules dynamically can work
 with them independently of what they actually do.

 The base behaviour is:
   plugin = Plugin(options)
   plugin.set_data(list(...))
   plugin.run()
   plugin.get_value('mean')
   plugin.get_value('stdev')
"""

from abc import ABCMeta, abstractmethod
import numpy as np

class AnalysisBase(metaclass=ABCMeta):
    """Base class for all analysis passes"""
    def __init__(self, options):
        if options is None:
            options = dict()
        if not isinstance(options, dict):
            raise TypeError("Analysis options should be a dictionary")
        self.options = options
        self.results = dict()
        self.data = None
        self.done = False

    def set_data(self, data):
        """Validate and set data - a list of results"""
        if not isinstance(data, list):
            raise TypeError("Analysis data should be a list")
        if not data or not isinstance(data[0], float):
            raise ValueError("Analysis data should be float and not empty")
        self.data = np.array(data)

    def get_data(self):
        """Return current data (may be different than set_data)"""
        if self.data is None or not self.data.any():
            return list()
        return self.data

    @abstractmethod
    def _run(self):
        pass

    def run(self):
        """Validate data and calls derived class' _run()"""
        if self.data is None or not self.data.any:
            raise RuntimeError("Can't analyse without data")
        self._run()
        self.done = True

    def set_option(self, key, value):
        """Set / change key = value"""
        if not isinstance(key, str):
            raise TypeError("Key must be a string")
        if not key:
            raise ValueError("Key must not empty")
        self.options[key] = value

    def get_value(self, key):
        """Return the value of the property named key"""
        if not isinstance(key, str):
            raise TypeError("Key must be a string")
        if not key:
            raise ValueError("Key must not empty")
        if key in self.results:
            return self.results[key]
        return ''
