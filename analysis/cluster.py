"""
 Cluster Module - group 1D data in clusters using K-Means

 Usage:
   clus = Clustering([...data...])
   clus.kmeans(3)
   print(repr(clus.get_outliers())

 Ideas:
  - http://scikit-learn.org/stable/modules/clustering.html
"""

import numpy as np
from outlier import Outliers

class Cluster:
    """Data class with a specific cluster"""
    def __init__(self, centre):
        self.data = list()
        self.centre = float(centre)

    def set_points(self, points):
        """Override data, returns true if centre changed"""
        if not isinstance(points, list):
            raise TypeError("Cluster points must be of array type")
        self.data = points
        changed = False
        # Cluster can have no points
        if points:
            mean = np.mean(self.data)
        else:
            mean = float('nan')
        # If changed, return true
        if mean != self.centre:
            changed = True
        self.centre = mean
        return changed

    def get_outliers(self):
        """Uses Outlier module to find outliers, if any"""
        out = Outliers(self.data)
        return out.get_outliers()

    def __str__(self):
        """Class name, for lists"""
        return "Cluster"

    def __repr__(self):
        """Pretty-printing"""
        return "(" + repr(len(self.data)) + "@" + repr(self.centre) + ")"

class Clustering:
    """Utility class to calculate clustering in data sets"""
    def __init__(self, data, max_iter=10):
        self.data = np.array(data)
        self.clusters = list()
        self.max_iter = max_iter
        self.done = False

    def kmeans(self, num_clusters=1):
        """Find K clusters"""
        # Create K random centres
        for cent in range(num_clusters):
            self.clusters.append(Cluster(np.random.randint(np.min(self.data),
                                                           np.max(self.data))))
        # List of points and centres they belong to
        belongs = np.zeros(len(self.data), np.int)

        # While centres move around (or up to max_iter)
        for _ in range(self.max_iter):
            changed = False

            # Assign points to closest centre
            for pnt in range(len(self.data)):
                dist = [abs(self.data[pnt]-self.clusters[i].centre)
                        for i in range(num_clusters)]
                cluster = np.argmin(dist)
                belongs[pnt] = cluster

            # Add all points to each centre and move to its mean
            for cent in range(num_clusters):
                new_points = [self.data[j]
                              for j in range(len(self.data))
                              if belongs[j] == cent]
                changed |= self.clusters[cent].set_points(new_points)

            # If nothing changed, it's solved
            if not changed:
                break

        self.done = True
        return self.clusters

    def get_outliers(self):
        """Get all outliers of all clusters"""
        if not self.done:
            self.kmeans()
        outliers = list()
        for cluster in self.clusters:
            outliers.extend(cluster.get_outliers())
        return outliers

    def __str__(self):
        """Class name, for lists"""
        return "Clustering"

    def __repr__(self):
        """Pretty-printing"""
        string = "[ " + repr(len(self.clusters)) + " cluster(s) on "
        string += repr(len(self.data)) + " data points"
        if self.clusters:
            string += " -> ( "
            for cluster in self.clusters:
                string += repr(cluster) + " "
            string += ")"
        string += " ]"
        return string
