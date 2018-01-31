# Benchmark Scripts
Script/modules to interpret benchmark/profiling results.

## Introduction
This set of modules will parse `perf stat` results as well as benchmark numbers (via plugins) and run the results through a number of statistical analysis passes (outlier detection, clustering, curve fitting) to identify potential "low hanging fruits" on a large space of results.

The advantage of this method becomes clear when you don't have prior knowledge on what bottlenecks exist in a system, or when you have so many degrees of freedom / dimensions on your test matrix that it's impossible for humans to "get a feeling" for what numbers "look wrong".

This is the goal, at least. Getting there will require a lot of trial and error.

The design decisions for this script are:
1. **Flexible:** a plugin architecture is required to add benchmark result parsing as well as statistical analysis.
1. **Simple:** each plugin must be simple and the interfaces consistent
1. **Extensible:** not only new plugins for benchmarks and analysis, but also result categorisation ('data_string' argument)
1. **Fully automated:** users should worry about how to run the benchmarks and what each different choice means (compiler flags may be linear, or aggregate, number of cores scale up, etc).
1. **Low noise:** the output of the system should be as terse as the number of outliers
1. **Stable:** the output should be the same given the same input (ie. not using random)

## Structure
The Engine has a "Linux Perf" core parser in which plugins can be annexed (via the plugin parameter, -p option in aggregate.py). The perf output goes into **stderr** while the benchmark results go into **stdout**, and that separation is clear in the perf driver (this may change in the future, depending on benchmarks).

Each analysis plugin will be loaded based on the _data_string_ (-d in aggregate.py) and will be passed in a number of lists created from the automatic categorisation.

The automatic categorisation will look at log file names, organise them hierarchically by separators, build a tree, then, for each _category_, it'll look for the analysis associated (via -d) and then collect all relevant data (across/along) and pass it though the plugin.

What to do with the results is still uncerain, as there are many ways in which they can be analysed, and not all of them make sense. One could do everything, but then it would be hard to define what's a _real_ outlier and what's just an artifact of the structure.

## Testing
$ pip install pytest && ./test.sh

## Pending tasks
Major features missing:
* There is no automatic categorisation for the analysis passes created from the _data_string_
* Improve the _data_string_ to contain all info needed for each mode of analysis
* The statistical analysis is very crude and needs a lot more care in what an outlier is based on the analysis
* Actually use scipy statistical analysis modules instead of home-brewed

A few known issues:
* Clustering is using random centres, need to be more stable
* Analysis plugins are not all behaving the same, need to have a common base class
* PYTHONPATH needs to contain the _engine_ directory for now, needs a proper package structure
