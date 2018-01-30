#!/usr/bin/env python3

"""Testing script for Lulesh functionality"""

import unittest
import os
from os.path import dirname, abspath
from pathlib import Path
from linux_perf import LinuxPerf
from lulesh import LinuxPerfPlugin

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

class TestLulesh(unittest.TestCase):
    """Lulesh tests"""

    def test_lulesh(self):
        """Lulesh Test / Simple"""
        lul = LinuxPerfPlugin()
        lul.parse(RAW)

        size = int(lul.get_value('ProblemSize'))
        self.assertEqual(size, 10)

        elms = int(lul.get_value('Elements'))
        self.assertEqual(elms, 1000)

        threads = int(lul.get_value('Threads'))
        self.assertEqual(threads, 8)

        energy = float(lul.get_value('FinalEnergy'))
        self.assertEqual(energy, 2.720531e+04)

        diff1 = float(lul.get_value('MaxAbsDiff'))
        self.assertEqual(diff1, 1.591616e-12)

        diff2 = float(lul.get_value('TotalAbsDiff'))
        self.assertEqual(diff2, 1.948782e-11)

        diff3 = float(lul.get_value('MaxRelDiff'))
        self.assertEqual(diff3, 1.566182e-14)

    def test_reading_files(self):
        """Lulesh Test / Files"""
        lul = LinuxPerfPlugin()
        root = dirname(abspath(__file__)) + "/x86_64"
        for _, _, files in os.walk(root):
            for logfile in files:
                logfile = root + '/' + logfile
                lul.parse(Path(logfile).read_text())

                size = int(lul.get_value('ProblemSize'))
                self.assertEqual(size, 50)

                elements = int(lul.get_value('Elements'))
                self.assertEqual(elements, 125000)

                fom = float(lul.get_value('FOM'))
                self.assertTrue(fom > 950 and fom < 2600)

                actual_threads = int((logfile.replace('.log', '')).split('-')[3])
                threads = int(lul.get_value('Threads'))
                self.assertEqual(threads, actual_threads)

    def test_errors(self):
        """Lulesh Test / Errors"""
        lul = LinuxPerfPlugin()

        lul.parse(['not', 'a', 'str'])
        self.assertFalse(lul.data)

        lul.parse('FOM = 123')
        self.assertEqual(int(lul.get_value('FOM')), 123)
        self.assertFalse(lul.get_value('Grind'))

    def test_as_plugin(self):
        """Lulesh Test / Plugin"""
        lul = LinuxPerfPlugin()
        perf = LinuxPerf(plugin=lul)
        perf.parse(RAW)

        energy = float(perf.get_value('FinalEnergy'))
        self.assertEqual(energy, 2.720531e+04)

        diff1 = float(perf.get_value('MaxAbsDiff'))
        self.assertEqual(diff1, 1.591616e-12)

        diff2 = float(perf.get_value('TotalAbsDiff'))
        self.assertEqual(diff2, 1.948782e-11)

        diff3 = float(perf.get_value('MaxRelDiff'))
        self.assertEqual(diff3, 1.566182e-14)


if __name__ == '__main__':
    unittest.main()
