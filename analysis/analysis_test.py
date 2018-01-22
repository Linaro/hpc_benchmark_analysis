#!/usr/bin/env python3

"""Testing script for Outlier/Curve fit functionality"""

import unittest
import math
from outlier import Outliers
from cluster import Clustering

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

if __name__ == '__main__':
    unittest.main()
