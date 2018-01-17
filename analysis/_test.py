#!/usr/bin/env python3

"""Testing script for Outlier/Curve fit functionality"""

from outlier import Outliers

def _test_outlier_simple():
    print("Test Outlier simple: ", end='')

    # A random gausian distribution of 8 numbers + 2 outliers
    data = [-0.17924, 0.13555605, -0.71446764, -0.12500689,
            -0.02595668, -0.39844776, 0.29403318, 0.39041369,
            -5, 5]
    expected_outliers = [[-5], [+5]]

    out = Outliers(data)
    ave, dev = out.get_stats()
    assert ave == -0.06231160500000001, "Wrong average for initial set"
    assert dev == 2.2569022689792186, "Wrong deviation for initial set"

    out.find_outliers()
    assert out.num_outliers() == 2, "Wrong number of outliers"
    assert out.get_outliers() == expected_outliers, "Wrong outliers"
    assert len(out.get_data()) == 8, "Wrong number of data points"

    ave, dev = out.get_stats()
    assert ave == -0.07788950625, "Wrong average for final set"
    assert dev == 0.3402887885570986, "Wrong deviation for final set"

    print("PASS")

# Tests
_test_outlier_simple()
