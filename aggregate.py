#!/usr/bin/env python3
"""
 Aggregate benchmark results, in hierarchical order

 The assumptions about the data are listed in Data.py

 Comparisons:
  * Between leaf categories in same category
    - Example: O2 vs. O3 for GCC, O2 vs. O3 for LLVM (above)
  * Between same leaf category across different categories
    - Example: GCC-O2 vs. LLVM-O2, GCC-O3 vs. LLVM-O3

 Analyses:
  * Create a plugin architecture / configuration file that will have metadata
    about the specific benchmark
  * Understand what are the distributions (normal, exp, scaled) for each data
  * Calculate correlation coeficients
    - Curve fit data against numeric categories (1, 2, 4, 8, ...)
    - Calculate distance to "perfect scalability"
    - Compare fit with other categories
    - Outlier can spot best / worst, OMP cost? CPU migrations?
  * Detecting order of results
    - Put results in order, match expectations (O1, O2, O3)
    - Linear fit outliers can tell "best option" (better results for same effort)
    - Maybe we should also track compilation times?
  * Identify differences between runs
    - Compare every data point to similar nodes in different categories
    - Different compiler, same options
    - Outliers can show best / worst case to compare to others
  * Statisisc on comparisons (above):
    - Only two: return difference, mark if outside threshold
    - 3 ~ 4: return mean / stdev
    - 5+: return mean / stdev and outliers
  * Issues to look for
    - Comparing two compilers across multiple versions may skew data, increasing
      spread and spoiling outlier detection (ex. 1-1-2 vs 3-4-4) -> K-Means
    - Unlike threads, compiler options are hard to know the expected "order",
      so comparing the order between compilers is a way to detect poor passes
    - Knowing which analysis to do based on positional category is bad. Create
      an option to specify that, ex. --analysis=cluster,order,gaus,fit to do,
      from top to bottom category, k-means clustering (assuming multiple groups),
      ordering and comparing order across higher categories, take average/dev and
      spot outliers and thresholds, and finally curve-fit to whatever the category
      is (requiring it to be numeric).

 Example:
  * Lulesh -.- gcc -.- O2 .- 1 (core)
            |       |     '- 2 (cores)
            |       |     '- 4 (cores)
            |       '- O3 .- 1 (core)
            |       |     '- 2 (cores)
            |       |     '- 4 (cores)
            |       '- .. .- 1 (core)
            |             '- 2 (cores)
            |             '- 4 (cores)
            |
            '- llvm .- O2 .- 1 (core)
                    |     '- 2 (cores)
                    |     '- 4 (cores)
                    '- O3 .- 1 (core)
                    |     '- 2 (cores)
                    |     '- 4 (cores)
                    '- .. .- 1 (core)
                          '- 2 (cores)
                          '- 4 (cores)

  * Comparisons:
    * gcc  - O2: 1 vs 2 vs 4 (curve fit + correlation)
    * gcc  - O2 vs O3 vs ... (ordering + line fit + distance outlier)
    * gcc+O3 vs llvm+O3 vs ...+O3 (difference + outlier)
"""
import sys
import os
import importlib
import getopt
from pathlib import Path
from linux_perf.data import Data
from linux_perf.linux_perf import LinuxPerf

# Required
sys.path.append('analysis')
sys.path.append('linux_perf')

def load_plugin(plugin):
    """Loads module in plugin/plugin.py and return LinuxPerfClass object"""
    root = os.path.dirname(os.path.abspath(__file__)) + "/" + plugin
    if not os.path.isdir(root) or not os.path.isfile(root + "/" + plugin + ".py"):
        raise ValueError(plugin + " needs to be a directory with a module inside")
    sys.path.append(plugin)
    mod = importlib.import_module(plugin)
    return mod.LinuxPerfPlugin()

def process(log_dir, log_file, data, plugin):
    """Process a single log file, using plugins, update Data"""
    # Hardcoded "process" for Lulesh for now
    plugin = load_plugin(plugin)
    # Create an empty perf, as we won't execute, just parse
    app = LinuxPerf(plugin=plugin)
    # Open log file, pass it to LinuxPerf, parse
    raw = Path(log_dir + "/" + log_file).read_text()
    app.set_raw(raw)
    results = app.parse()
    # Collect parsed data, push into Data
    data.add_log(log_dir, log_file, results)

def process_logs(log_dir, data, plugin):
    """Process all log files in directory, update Data"""
    # Unused root, dirs, only reading files
    for _, _, files in os.walk(log_dir):
        for filename in files:
            if filename.startswith("."):
                continue
            process(log_dir, filename, data, plugin)

def process_runs(name, log_dirs, plugin, data_string):
    """Adjust dictionary, process all logs, return Data"""
    data = Data(name, data_string)
    # For each log dir, parse, append to the dictionary
    for log_dir in log_dirs:
        process_logs(log_dir, data, plugin)
    return data

def compare(data):
    """Compare all results together, mark exceptions"""
    # Find th leaf nodes (perf/bench data)
    # Find their equivalent leaf nodes in other categories
    # Spot outliers, curve fits, significant differences
    return data

def syntax():
    """Syntax"""
    print("Syntax: aggregate.py [options] benchname <logs_dir_arch1> <logs_dir_arch2> ...")
    print(" Options:")
    print("   -p <plugin_name> : Loads class LinuxPerfPlugin in module <plugin_name>")
    print("   -d <data_desc> : Description of the data, in positional order, in log names")
    print("                    Example: -d sep=-,outlier=1.0,cluster=2,fit=2")
    print("                             from lognames <compiler>-<options>-<arch>-<cores>")
    sys.exit(2)

def validate_plugin(plugin):
    """Make sure we don't try to load a bogus plugin"""
    filename = plugin + "/" + plugin + ".py"
    if os.path.isdir(plugin) and os.path.isfile(filename):
        raw = Path(filename).read_text()
        if raw.find("class LinuxPerfPlugin") == -1:
            print("Cannot find class LinuxPerfPlugin in " + filename)
            syntax()
    else:
        print("Cannot find plugin " + filename)
        syntax()

def main():
    """Main"""
    # All options come first
    start = 1
    plugin = None
    data_string = ''
    opts, _ = getopt.getopt(sys.argv[start:], 'p:d:')
    for opt, arg in opts:
        if opt in ('-p', '--plugin'):
            validate_plugin(arg)
            plugin = arg
            start += 2
        elif opt in ('-d', '--data'):
            data_string = arg
            start += 2
        else:
            syntax()

    # First positional parameter is benchmark name
    if len(sys.argv) < start+1:
        print("Missing Benchmark name")
        syntax()
    benchname = sys.argv[start]
    if not benchname:
        syntax()
    start += 1

    # Second onward is different runs' logs (machines?)
    if len(sys.argv) < start+1:
        print("Needs at least one log directory")
        syntax()
    log_dirs = sys.argv[start:]
    if not log_dirs:
        syntax()

    # Validate input
    for log_dir in log_dirs:
        if not os.path.isdir(log_dir):
            print(log_dir + " is not a directory")
            syntax()

    # Process all logs (with plugins)
    data = process_runs(benchname, log_dirs, plugin, data_string)

    # Perform all comparisons
    data.summary()
    compare(data)

    # Dump significant data (higher than threshold)

if __name__ == "__main__":
    main()
