"""
 Curve Fit - Fits data to expected curves, calculates goodness of fit

 Usage:
   fit = CurveFit([1, 2, 3], [.9, 2.1, 3.05], 1)
   fit.fit()
   print("Quality of fit: " + fit.quality([1, 2, 3]))

 Ideas:
  - https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.chisquare.html

"""

import numpy as np

class CurveFit:
    """Curve Fit"""
    def __init__(self, x, y, degree=1):
        if not isinstance(x, list):
            raise "X must be a list"
        if not isinstance(y, list):
            raise "Y must be a list"
        if len(x) != len(y):
            raise "X and Y must have same length"

        self.xval = np.array(x)
        self.yval = np.array(y)
        self.degree = degree
        self.residual = None
        self.poly = None

    def fit(self):
        """Poly fit"""
        self.poly = np.polyfit(self.xval, self.yval, self.degree)
        self.residual = np.polyval(self.poly, self.xval)

    def quality(self, optimal):
        """Compares the current fit to the expected 'optimal'
           The higher the value, the worse the fit is"""
        if not isinstance(optimal, list):
            raise "Optimal must be a list"
        if len(self.xval) != len(optimal):
            raise "X and optimal must have same length"
        optp = np.polyfit(self.xval, optimal, self.degree)
        optr = np.polyval(optp, self.xval)
        # Assumes expected is mean of observed (see scipy)
        return float(np.sum(((optr-self.residual)**2)/np.mean(self.yval)))
