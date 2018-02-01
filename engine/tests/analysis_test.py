#!/usr/bin/env python3

"""Testing script for Outlier/Curve fit functionality"""

import unittest
from analysis.outlier import Outliers
from analysis.cluster import Clustering
from analysis.fit import CurveFit

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

        out = Outliers()
        out.set_data(data)
        ave = out.get_value('mean')
        dev = out.get_value('stdev')
        self.assertEqual(ave, -0.06231160500000001)
        self.assertEqual(dev, 2.2569022689792186)

        out.run()

        num_outliers = out.get_value('num_outliers')
        outliers = out.get_value('outliers')
        self.assertEqual(num_outliers, 2)
        self.assertEqual(outliers, expected_outliers)
        self.assertEqual(len(out.get_data()), 8)

        ave = out.get_value('mean')
        dev = out.get_value('stdev')
        self.assertEqual(ave, -0.07788950625)
        self.assertEqual(dev, 0.3402887885570986)

    def test_outlier_small(self):
        """Outlier Test / Smal"""

        # A data too smal to have outliers
        out = Outliers()
        out.set_data([1., 2.])
        ave = out.get_value('mean')
        self.assertEqual(ave, 1.5)
        dev = out.get_value('stdev')
        self.assertEqual(dev, 0.5)
        scale = out.get_value('scale')
        self.assertEqual(scale, 2.0)
        outliers = out.get_value('outliers')
        self.assertEqual(outliers, '')

    def test_clustering_simple(self):
        """Clustering Test / Simple"""

        # A random gausian distribution of 8 numbers
        data = [-0.17924, 0.13555605, -0.71446764, -0.12500689,
                -0.02595668, -0.39844776, 0.29403318, 0.39041369]
        # One additional distribution
        new = list()
        for dat in data:
            new.append(dat-3)
            new.append(dat+3)
        data.extend(new)

        clustering = Clustering()
        clustering.set_data(data)
        clustering.set_option('num_clusters', 3)
        clustering.run()
        clusters = clustering.get_value('clusters')
        self.assertEqual(len(clusters), 3)

        self.assertEqual(clusters[0].centre, -3.07788950625)
        self.assertEqual(clusters[1].centre, -0.07788950625)
        self.assertEqual(clusters[2].centre, 2.92211049375)

    def test_clustering_outlier(self):
        """Clustering Test / Outlier"""

        # A random gausian distribution of 8 numbers
        data = [-0.17924, 0.13555605, -0.71446764, -0.12500689,
                -0.02595668, -0.39844776, 0.29403318, 0.39041369]
        # + 2 outliers
        expected_outliers = [[-5], [+5]]
        for out in expected_outliers:
            data.append(out[0])

        clustering = Clustering()
        clustering.set_data(data)
        clustering.set_option('num_clusters', 1)
        clustering.run()
        clusters = clustering.get_value('clusters')
        self.assertEqual(len(clusters), 1)

        self.assertEqual(clusters[0].centre, -0.06231160500000001)
        self.assertEqual(clusters[0].get_outliers(), expected_outliers)

    def test_curve_fit_simple(self):
        """Curve Fit Test / Simple"""

        # X axis is the same for all
        xval = [0, 1, 2, 3, 4, 5]
        # Linear points
        linear = [.1, .9, 1.85, 2.77, 3.69, 4.54]
        linfit = CurveFit({'degree': 1, 'optimal': xval})
        linfit.set_data(linear)
        linfit.run()
        poly = linfit.get_value('poly')
        self.assertEqual(poly[1], 0.0590476190476186)
        self.assertEqual(poly[0], 0.8997142857142856)
        self.assertEqual(linfit.get_value('quality'), 0.17173347086126853)

        # Quadractic
        quad = [.2, 1.1, 3.98, 8.88, 15.4, 24.2]
        optimal = [0, 1, 4, 9, 16, 25]
        quadfit = CurveFit({'degree':2, 'xaxix':xval, 'optimal':optimal})
        quadfit.set_data(quad)
        quadfit.run()
        poly = quadfit.get_value('poly')
        self.assertEqual(poly[2], 0.1921428571428483)
        self.assertEqual(poly[1], -0.03249999999999286)
        self.assertEqual(poly[0], 0.9653571428571415)
        self.assertEqual(quadfit.get_value('quality'), 0.11625478316326478)

        # Comparison between linear and quad should be bad
        quadfit.set_option('optimal', xval)
        self.assertEqual(quadfit.get_value('quality'), 59.94661192602033)


if __name__ == '__main__':
    unittest.main()
