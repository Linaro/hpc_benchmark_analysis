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

class Outliers:
    """Utility class to calculate outliers in data sets"""
    def __init__(self, data, threshold=3.5):
        """Data is number array, max_outliers = 0 means unlimited"""
        self.data = np.array(data)
        # We store the stdev on the second axis
        if len(self.data.shape) == 1:
            self.data = self.data[:, None]
        self.outliers = None
        self.threshold = threshold
        self.done = False

    def get_stats(self):
        """Get average/stdev of the current data"""
        average = 0
        deviation = 0
        if self.data.any:
            average = np.mean(self.data)
            deviation = np.std(self.data)
        return average, deviation

    def num_outliers(self):
        """Count outliers in dataset"""
        if not self.done:
            self.find_outliers()
        return np.count_nonzero(self.outliers)

    def get_data(self):
        """Return data as list"""
        if not self.done:
            self.find_outliers()
        return self.data.tolist()

    def get_outliers(self):
        """Return outliers in dataset as list"""
        if not self.done:
            self.find_outliers()
        return self.outliers.tolist()

    def find_outliers(self):
        """MED based outliser test (better than percentile, see source)"""
        # G = MAX(Xi - Xmed)/dev
        median = np.median(self.data, axis=0)
        diff = np.sqrt(np.sum((self.data - median)**2, axis=-1))

        # Mi = 0.6745(Xi - Xmed)/MAD
        mad = np.median(diff)
        mzs = 0.6745 * diff / mad

        # Return array with bits set on which are the outliers
        outliers_flags = mzs > self.threshold

        # Remove outliers from data
        self.outliers = self.data[outliers_flags]
        self.data = self.data[np.logical_not(outliers_flags)]

        self.done = True

    def __str__(self):
        """Class name, for lists"""
        return "Outliers"

    def __repr__(self):
        """Pretty-printing"""
        string = "[ " + repr(self.threshold) + " found "
        if self.outliers:
            string += repr(len(self.outliers)) + " outliers on "
            if self.outliers.any():
                string += " -> ( "
                for out in self.outliers:
                    string += repr(out[0]) + " "
                string += ")"
        if self.data:
            string += repr(len(self.data)) + " data points"
        string += " ]"
        return string
