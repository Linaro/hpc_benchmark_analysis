"""
 Outlier Module - detect outliers based on the Grubs test [1].
 According to [2], threshold is 3.5 and MZS=0.6745(Xi-Xmed)/MAD

 Usage:
   out = Outlier([...data...], significance)
   out.find_outliers()
   print(repr(out.outliers))

 [1] http://www.itl.nist.gov/div898/handbook/eda/section3/eda35h1.htm
 [2] Boris Iglewicz and David Hoaglin (1993)
     "Volume 16: How to Detect and Handle Outliers"
     The ASQC Basic References in Quality Control: Statistical Techniques
     Edward F. Mykytka, Ph.D., Editor.
"""

import numpy as np
from analysis.base import AnalysisBase

class Outliers(AnalysisBase):
    """Utility class to calculate outliers in data sets"""
    def __init__(self, options=None):
        super().__init__(options)
        # Mandatory options
        if 'threshold' in self.options:
            if not isinstance(self.options['threshold'], float):
                raise ValueError("Threshold must be float")
        else:
            self.options['threshold'] = 3.5 # recommended default value

    def set_data(self, data):
        """Sets data, makes sure np.array is in the right shape"""
        super().set_data(data)
        # We store the stdev on the second axis
        if len(self.data.shape) == 1:
            self.data = self.data[:, None]
        self.results['mean'] = np.mean(self.data)
        self.results['stdev'] = np.std(self.data)

    def _run(self):
        """MED based outlier test (better than percentile, see source)"""
        # G = MAX(Xi - Xmed)/dev
        median = np.median(self.data, axis=0)
        diff = np.sqrt(np.sum((self.data - median)**2, axis=-1))

        # Mi = 0.6745(Xi - Xmed)/MAD
        mad = np.median(diff)
        mzs = 0.6745 * diff / mad

        # Return array with bits set on which are the outliers
        outliers_flags = mzs > self.options['threshold']

        # Store results
        self.results['outliers'] = self.data[outliers_flags].tolist()
        self.results['num_outliers'] = np.count_nonzero(self.results['outliers'])

        # Remove outliers from data
        self.data = self.data[np.logical_not(outliers_flags)]
        self.results['mean'] = np.mean(self.data)
        self.results['stdev'] = np.std(self.data)

        self.done = True

    def __str__(self):
        """Class name, for lists"""
        return "Outliers"

    def __repr__(self):
        """Pretty-printing"""
        string = "[ " + repr(self.results['threshold']) + " found "
        if 'outliers' in self.results:
            string += repr(len(self.results['outliers'])) + " outliers on "
            if self.results['outliers']:
                string += " -> ( "
                for out in self.results['outliers']:
                    string += repr(out[0]) + " "
                string += ")"
        if self.data:
            string += repr(len(self.data)) + " data points"
        string += " ]"
        return string
