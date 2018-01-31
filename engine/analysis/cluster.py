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
from analysis.outlier import Outliers
from analysis.outlier import AnalysisBase

class Cluster:
    """Data class with a specific cluster"""
    def __init__(self, centre):
        self.data = list()
        self.centre = float(centre)

    def set_data(self, data):
        """Override data, returns true if centre changed"""
        if not isinstance(data, list):
            raise TypeError("Cluster points must be of array type")
        self.data = data
        changed = False
        # Cluster can have no points
        if self.data:
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
        out = Outliers()
        out.set_data(self.data)
        out.run()
        return out.get_value('outliers')

    def __str__(self):
        """Class name, for lists"""
        return "Cluster"

    def __repr__(self):
        """Pretty-printing"""
        return "(" + repr(len(self.data)) + "@" + repr(self.centre) + ")"

class Clustering(AnalysisBase):
    """Utility class to calculate clustering in data sets"""
    def __init__(self, options=None):
        super().__init__(options)
        # Mandatory options
        self.results['clusters'] = list()
        self.results['outliers'] = list()
        self.max_iter = 10 # number of attempts
        if 'num_clusters' in self.options:
            if not isinstance(self.options['num_clusters'], int):
                raise ValueError("Threshold must be int")
        else:
            self.options['num_clusters'] = 1

    def _run(self):
        """Find K clusters"""
        num_clusters = self.options['num_clusters']

        # Create K exclusive equidistant centres (x o o o x)
        centres = np.linspace(np.min(self.data), np.max(self.data),
                              num_clusters+1, False)
        centres = np.delete(centres, 0) # avoid first outlier
        for cent in centres:
            self.results['clusters'].append(Cluster(cent))
        # List of points and centres they belong to
        belongs = np.zeros(len(self.data), np.int)

        # While centres move around (or up to max_iter)
        for _ in range(self.max_iter):
            changed = False

            # Assign points to closest centre
            for pnt in range(len(self.data)):
                dist = [abs(self.data[pnt]-self.results['clusters'][i].centre)
                        for i in range(num_clusters)]
                cluster = np.argmin(dist)
                belongs[pnt] = cluster

            # Add all points to each centre and move to its mean
            for cent in range(num_clusters):
                new_points = [self.data[j]
                              for j in range(len(self.data))
                              if belongs[j] == cent]
                changed |= self.results['clusters'][cent].set_data(new_points)

            # If nothing changed, it's solved
            if not changed:
                break

        # Find outliers on each cluster
        for cluster in self.results['clusters']:
            self.results['outliers'].extend(cluster.get_outliers())

    def __str__(self):
        """Class name, for lists"""
        return "Clustering"

    def __repr__(self):
        """Pretty-printing"""
        string = "[ " + repr(len(self.results['clusters'])) + " cluster(s) on "
        string += repr(len(self.data)) + " data points"
        if self.results['clusters']:
            string += " -> ( "
            for cluster in self.results['clusters']:
                string += repr(cluster) + " "
            string += ")"
        string += " ]"
        return string
