# Data Analysis

These modules are built to automatically discover outliers on multi-dimensional data. For that reason, they have to be robust and flexible, but also expect somewhat rigid structure from the data set. This is not machine learning, just statistical analysis.

## Flexibility

Flexibility is about how each analysis plugin operates. They need to require little to no input other than the data itself, and output as much as it can about its own internal processes (ex. hoe many clusters it found, what were the outliers, etc). In the current design, the base plugin has two methods: `set_option` and `get_value`, respectively, input and output.

The plugins need to be resilient to input, though. If no fixed number of clusters or polynomial degree is passed, then try a few and pick the best value (closest grouping, lowest deviation, best fit, etc), then save on results all of the decisions, so that users can grab those via `get_value`.

## Expectations

The expectations are mostly about the dataset. The categories should be the same, in the same order, across all runs. So, if you are testing GCC and LLVM on multiple versions with multiple options (same set of options for both), then they all need to be in the same order, with the same information.

Again, this needs to be resilient, so the sets will be stored in a format that will make it easy to find maximum common sub-trees, but if the categories are not in the same order, then the common parts will end up being an empty set.

Also, the last category will have the data in dictionary form (created by the parsers: perf, benchmark plugins, yaml files, etc). That data should *also* be the same (same keys, case-sesitive), or the analysis will ignore them and end up empty, too.

## Across / Along analysis

The key to this method is indicating what categories (say compiler, options, number of cores) is to be measured across (for different compilers, pick all -O3 runs) or along (for the same compiler/option, compare different number of cores). Obviously, the analysis to be done in each case are different. Most likely, across analysis will end up being clustering, detecting outliers or just measuring compatibility via standard deviation/mean distances, while along analysis are more likely curve fitting and fit quality testing.

However, once the first grouping and analysis is done, we end up with a large number of groups statistics, and they can be compared again, with the opposite strategy!

So, for example, comparing benchmark numbers between GCC and LLVM, O2 and O3, from 1, 2, and 4 cores would give us the tree:

```
    GCC           LLVM
 O2     O3      O2     O3
1,2,4  1,2,4   1,2,4  1,2,4
```

If we set `Compiler = Clustering(across)`, `Options = Clustering(across)`, `Cores = Fit(along)`, we'll end up with the following sets:

```
Compiler = Clustering: { gcc-O2-1, llvm-O2-1 }, { gcc-O3-1, llvm-O3-1 }, ... { gcc-O3-4, llvm-O3-4 }; (6 groups)
 Options = Clustering: { gcc-O2-1, gcc-O3-1 },  { gcc-O3-2, gcc-O3-2 },  ... { llvm-O2-4, llvm-O3-4 }; (6 groups)
   Cores =   CurveFit: { gcc-O2-1, gcc-O2-2, gcc-O2-4 }, ... { llvm-O3-1, llvm-O3-2, llvm-O3-4 }; (4 groups)
```

Each group has its own mean-stdev / fit-quality, which are, themselves, data that can be compared again. Note that, upon inspection, because we didn't cluster 1-core with 2 and 4-core runs, now each two of the 6 group set form a group on their own, and the three super-groups can be analysed _along_ using curve fit.

The same is true for the core analysis, as each fit has a quality measure (we assume towards the same fit - number of cores), so they can also be clustered and outliers can be found.

## Returning results

There are two important results that can come out of an analysis like this: data visualisation and outlier detection.

### Data Visualisation

For each set, group and super-groups, we can plot the graphs, with standard deviation and nice legends/axis labels, using any of Python's good plotting libraries, and save the images locally, so that developers can peruse the results in a visual form and infer things that perhaps our automated analysis missed.

An addition dump of the data can be interesting for evolution analysis, trend/spike detection, etc. Those analysis can already be done by tools like LLVM's LNT infrastructure, and converting the data to their format would be an interesting plugin to add.

## Outlier Detection

However, perhaps the most powerful result would be printing the biggest outliers of the dataset. This cna be done simply by printing a list at the end of the run, and when done on dispatchers (like Jenkins, Travis or Buildbots), it would be at the very end of the log, being very easy to spot anomalies and comparing to previous runs.
