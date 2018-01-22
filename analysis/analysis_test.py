#!/usr/bin/env python3

"""Testing script for Outlier/Curve fit functionality"""

import unittest
import math
from outlier import Outliers
from cluster import Clustering
from fit import CurveFit

class TestAnalysis(unittest.TestCase):
    """Analysys tests"""

    def test_outlier_simple(self):
        """Outlier Test / Simple"""

        # A random gausian distribution of 8 numbers
        data = [-0.17924, 0.13555605, -0.71446764, -0.12500689,
                -0.02595668, -0.39844776, 0.29403318, 0.39041369]
        # + 2 outliers
        expected_outliers = [[-5], [+5]]
        for out in expected_outliers:
            data.append(out[0])

        out = Outliers(data)
        ave, dev = out.get_stats()
        self.assertEqual(ave, -0.06231160500000001)
        self.assertEqual(dev, 2.2569022689792186)

        out.find_outliers()
        self.assertEqual(out.num_outliers(), 2)
        self.assertEqual(out.get_outliers(), expected_outliers)
        self.assertEqual(len(out.get_data()), 8)

        ave, dev = out.get_stats()
        self.assertEqual(ave, -0.07788950625)
        self.assertEqual(dev, 0.3402887885570986)

    def test_clustering_simple(self):
        """Clustering Test / Simple"""

        # A random gausian distribution of 8 numbers
        data = [-0.17924, 0.13555605, -0.71446764, -0.12500689,
                -0.02595668, -0.39844776, 0.29403318, 0.39041369]
        # One additional distribution
        new = list()
        for dat in data:
            new.append(dat+3)
        data.extend(new)

        clustering = Clustering(data)
        clusters = clustering.kmeans(2)
        self.assertEqual(len(clusters), 2)

        # Clustering involves randomness, and this example exhibits two behaviours
        # (float('nan'), 1.42211049375),
        # (-0.07788950625, 2.92211049375)
        match = False
        for idx, cluster in enumerate(clusters):
            if (math.isnan(cluster.centre) and
                    clusters[1-idx].centre == 1.42211049375):
                match = True
                break
            if (cluster.centre == -0.07788950625 and
                    clusters[1-idx].centre == 2.92211049375):
                match = True
                break
        self.assertTrue(match)

    def test_clustering_outlier(self):
        """Clustering Test / Outlier"""

        # A random gausian distribution of 8 numbers
        data = [-0.17924, 0.13555605, -0.71446764, -0.12500689,
                -0.02595668, -0.39844776, 0.29403318, 0.39041369]
        # + 2 outliers
        expected_outliers = [[-5], [+5]]
        for out in expected_outliers:
            data.append(out[0])

        clustering = Clustering(data)
        clusters = clustering.kmeans(1)
        self.assertEqual(len(clusters), 1)

        self.assertEqual(clusters[0].centre, -0.06231160500000001)
        self.assertEqual(clusters[0].get_outliers(), expected_outliers)

    def test_curve_fit_simple(self):
        """Curve Fit Test / Simple"""

        # X axis is the same for all
        xval = [0, 1, 2, 3, 4, 5]
        # Linear points
        linear = [.1, .9, 1.85, 2.77, 3.69, 4.54]
        linfit = CurveFit(xval, linear)
        linfit.fit()
        self.assertEqual(linfit.poly[1], 0.0590476190476186)
        self.assertEqual(linfit.poly[0], 0.8997142857142856)
        optimal = xval # linear
        self.assertEqual(linfit.quality(optimal), 0.17173347086126853)

        # Quadractic
        quad = [.2, 1.1, 3.98, 8.88, 15.4, 24.2]
        quadfit = CurveFit(xval, quad, 2)
        quadfit.fit()
        self.assertEqual(quadfit.poly[2], 0.1921428571428483)
        self.assertEqual(quadfit.poly[1], -0.03249999999999286)
        self.assertEqual(quadfit.poly[0], 0.9653571428571415)
        optimal = [0, 1, 4, 9, 16, 25]
        self.assertEqual(quadfit.quality(optimal), 0.11625478316326478)

        # Comparison between linear and quad should be bad
        self.assertEqual(quadfit.quality(xval), 59.94661192602033)


if __name__ == '__main__':
    unittest.main()
