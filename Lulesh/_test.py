#!/usr/bin/env python3

"""Testing script for Lulesh functionality"""

import os
from pathlib import Path
from lulesh import LuleshPerf

RAW = """Running problem size 10^3 per domain until completion
Num processors: 1
Num threads: 8
Total number of elements: 1000

To run other sizes, use -s <integer>.
To run a fixed number of iterations, use -i <integer>.
To run a more or less balanced region set, use -b <integer>.
To change the relative costs of regions, use -c <integer>.
To print out progress, use -p
To write an output file for VisIt, use -v
See help (-h) for more options

Run completed:  
   Problem size        =  10 
   MPI tasks           =  1 
   Iteration count     =  231 
   Final Origin Energy = 2.720531e+04 
   Testing Plane 0 of Energy Array on rank 0:
        MaxAbsDiff   = 1.591616e-12
        TotalAbsDiff = 1.948782e-11
        MaxRelDiff   = 1.566182e-14


Elapsed time         =       0.24 (s)
Grind time (us/z/c)  =  1.0388182 (per dom)  ( 1.0388182 overall)
FOM                  =  962.63236 (z/s)"""

def _test_lulesh():
    print("Lulesh Test / Simple: ", end='')
    lul = LuleshPerf()
    lul.parse(RAW)

    size = int(lul.get_value('ProblemSize'))
    assert size == 10, 'Wrong size'

    elms = int(lul.get_value('Elements'))
    assert elms == 1000, 'Wrong number of elements'

    threads = int(lul.get_value('Threads'))
    assert threads == 8, 'Wrong number of threads'

    energy = float(lul.get_value('FinalEnergy'))
    assert energy == 2.720531e+04, 'Wrong energy'

    diff1 = float(lul.get_value('MaxAbsDiff'))
    assert diff1 == 1.591616e-12, 'Wrong MaxAbsDiff'

    diff2 = float(lul.get_value('TotalAbsDiff'))
    assert diff2 == 1.948782e-11, 'Wrong TotalAbsDiff'

    diff3 = float(lul.get_value('MaxRelDiff'))
    assert diff3 == 1.566182e-14, 'Wrong MaxRelDiff'

    print("PASS")

def _test_reading_files():
    print("Lulesh Test / Files: ", end='')
    lul = LuleshPerf()
    root = os.path.dirname(os.path.abspath(__file__)) + "/x86_64"
    for _, _, files in os.walk(root):
        for logfile in files:
            logfile = root + '/' + logfile
            lul.parse(Path(logfile).read_text())

            size = int(lul.get_value('ProblemSize'))
            assert size == 50, 'Wrong size'

            elements = int(lul.get_value('Elements'))
            assert elements == 125000, 'Wrong number of elements'

            fom = float(lul.get_value('FOM'))
            assert (fom > 950 and fom < 2600), 'Wrong range for FOM'

            actual_threads = int((logfile.replace('.log', '')).split('-')[3])
            threads = int(lul.get_value('Threads'))
            assert threads == actual_threads, "Wrong number of threads"

    print("PASS")

def _test_errors():
    print("Lulesh Test / Errors: ", end='')
    lul = LuleshPerf()

    lul.parse(['not', 'a', 'str'])
    assert not lul.data, "Should not have parsed list"

    lul.parse('FOM = 123')
    assert int(lul.get_value('FOM')) == 123, "Should have FOM"
    assert not lul.get_value('Grind'), "Should not have Grind"

    print("PASS")

# Tests
_test_lulesh()
_test_reading_files()
_test_errors()
