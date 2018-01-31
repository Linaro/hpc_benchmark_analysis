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
from analysis.outlier import AnalysisBase

class CurveFit(AnalysisBase):
    """Curve Fit"""
    def __init__(self, options):
        super().__init__(options)
        self.residual = None
        self.poly = None

    def _xaxis(self):
        if 'xaxis' in self.options:
            xaxis = self.options['xaxis']
            if not isinstance(self.data, list) or len(self.data) != len(xaxis):
                raise ValueError("'xaxis' must have the same length as data")
        else:
            xaxis = np.linspace(0, len(self.data)-1, len(self.data), dtype=int)
        return xaxis

    def _quality(self):
        """Compares the current fit to the self.data 'optimal'
           The higher the value, the worse the fit is"""
        if 'optimal' not in self.options:
            return 0.0
        optimal = self.options['optimal']
        if not isinstance(optimal, list):
            raise TypeError("Optimal must be a list")
        xaxis = self._xaxis()
        if len(xaxis) != len(optimal):
            raise ValueError("'xaxis' and optimal must have same length")
        degree = self.options['degree']
        optp = np.polyfit(xaxis, optimal, degree)
        optr = np.polyval(optp, xaxis)
        # Assumes self.data is mean of observed (see scipy)
        residual = self.results['residual']
        return float(np.sum(((optr-residual)**2)/np.mean(self.data)))

    def _run(self):
        """Poly fit"""
        if 'degree' not in self.options:
            raise RuntimeError("Curve fit needs 'degree' options set")
        degree = self.options['degree']
        if not isinstance(degree, int) or degree < 1:
            raise ValueError("degree must be integer > 1")

        xaxis = self._xaxis()
        poly = np.polyfit(xaxis, self.data, degree)
        residual = np.polyval(poly, xaxis)

        self.results['poly'] = poly
        self.results['residual'] = residual
        self.results['quality'] = self._quality()

    def get_value(self, key):
        """Specialise to recalculate quality, optimal may have changed"""
        if key == 'quality' and self.done:
            self.results['quality'] = self._quality()
        return super().get_value(key)

    def __str__(self):
        """Class name, for lists"""
        return "CurveFit"

    def __repr__(self):
        """Pretty-printing"""
        string = "[ " + repr(self.poly) + ", " + repr(self.residual) + " ]"
        return string
