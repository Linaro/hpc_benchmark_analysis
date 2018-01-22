"""Curve Fit"""

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

    def get(self, xval):
        """Gets the estimated Y value for X"""
        return self.poly(xval)

    def compare(self, optimal):
        """Compares the current fit to the expected 'optimal'"""
        if not isinstance(optimal, list):
            raise "Optimal must be a list"
        if len(self.xval) != len(optimal):
            raise "X and optimal must have same length"
        optp = np.polyfit(self.xval, optimal, self.degree)
        optr = np.polyval(optp, self.xval)
        return float(np.mean(abs(optr-self.residual)))
