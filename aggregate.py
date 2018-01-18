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
  * Calculate correlation coeficients, detect outliers, etc.
"""
import sys
import os
from pathlib import Path
from data import Data
from linux_perf.linux_perf import LinuxPerf
from Lulesh.lulesh import LuleshPerf

def process(log_dir, log_file, data):
    """Process a single log file, using plugins, update Data"""
    # Hardcoded "process" for Lulesh for now
    plugin = LuleshPerf()
    # Create an empty perf, as we won't execute, just parse
    app = LinuxPerf([''], plugin)
    # Open log file, pass it to LinuxPerf, parse
    raw = Path(log_dir + "/" + log_file).read_text()
    app.set_raw(raw)
    results = app.parse()
    # Collect parsed data, push into Data
    data.add_log(log_dir, log_file, results)

def process_logs(log_dir, data):
    """Process all log files in directory, update Data"""
    # Unused root, dirs, only reading files
    for _, _, files in os.walk(log_dir):
        for filename in files:
            if filename.startswith("."):
                continue
            process(log_dir, filename, data)

def process_runs(name, log_dirs):
    """Adjust dictionary, process all logs, return Data"""
    data = Data(name)
    # For each log dir, parse, append to the dictionary
    for log_dir in log_dirs:
        process_logs(log_dir, data)
    return data

def syntax():
    """Syntax"""
    print("Syntax: aggregate.py benchname <logs_dir_arch1> <logs_dir_arch2> ...")
    sys.exit(2)

def main():
    """Main"""
    # First parameter is benchmark name
    benchname = sys.argv[1]
    if not benchname:
        syntax()
    # Second onward is different runs' logs (machines?)
    log_dirs = sys.argv[2:]
    if not log_dirs:
        syntax()
    # Validate input
    for log_dir in log_dirs:
        if not os.path.isdir(log_dir):
            print(log_dir + " is not a directory")
            syntax()
    # Process all logs
    data = process_runs(benchname, log_dirs)
    data.summary()

if __name__ == "__main__":
    main()
