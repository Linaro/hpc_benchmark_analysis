#!/usr/bin/env python3

"""Testing script for Outlier/Curve fit functionality"""

import math
from outlier import Outliers
from cluster import Clustering

def _test_outlier_simple():
    print("Outlier Test / Simple: ", end='')

    # A random gausian distribution of 8 numbers
    data = [-0.17924, 0.13555605, -0.71446764, -0.12500689,
            -0.02595668, -0.39844776, 0.29403318, 0.39041369]
    # + 2 outliers
    expected_outliers = [[-5], [+5]]
    for out in expected_outliers:
        data.append(out[0])

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

def _test_clustering_simple():
    print("Clustering Test / Simple: ", end='')

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
    assert len(clusters) == 2, "Wrong number of clusters"

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
    assert match, "Wrong clusters configuration"

    print("PASS")

def _test_clustering_outlier():
    print("Clustering Test / Outlier: ", end='')

    # A random gausian distribution of 8 numbers
    data = [-0.17924, 0.13555605, -0.71446764, -0.12500689,
            -0.02595668, -0.39844776, 0.29403318, 0.39041369]
    # + 2 outliers
    expected_outliers = [[-5], [+5]]
    for out in expected_outliers:
        data.append(out[0])

    clustering = Clustering(data)
    clusters = clustering.kmeans(1)
    assert len(clusters) == 1, "Wrong number of clusters"

    assert clusters[0].centre == -0.06231160500000001, "Wrong cluster centre"
    assert clusters[0].get_outliers() == expected_outliers, "Wrong outliers"

    print("PASS")

# Tests
_test_outlier_simple()
_test_clustering_simple()
_test_clustering_outlier()
