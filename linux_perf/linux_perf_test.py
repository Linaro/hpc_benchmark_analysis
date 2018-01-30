#!/usr/bin/env python3

"""Testing script for linux_perf functionality"""

import unittest
import os
from pathlib import Path
from linux_perf import LinuxPerf, PerfData
from data import Data

RAW = """
 Performance counter stats for 'date':

          0.735081      task-clock:u (msec)       #    0.651 CPUs utilized
                 0      context-switches:u        #    0.000 K/sec
                 0      cpu-migrations:u          #    0.000 K/sec
                60      page-faults:u             #    0.082 M/sec
           383,614      cycles:u                  #    0.522 GHz
           300,826      instructions:u            #    0.78  insn per cycle
            65,455      branches:u                #   89.045 M/sec
             5,202      branch-misses:u           #    7.95% of all branches

       0.001128531 seconds time elapsed
"""

class TestLinuxPerf(unittest.TestCase):
    """LinuxPerf tests"""

    def test_raw(self):
        """LinuxPerf Test / Raw"""
        raw = LinuxPerf()
        raw.set_raw(RAW)
        raw.parse()

        inst = int(raw.get_value('instructions'))
        self.assertEqual(inst, 300826)

        branches = int(raw.get_value('branches'))
        self.assertEqual(branches, 65455)

        elapsed = float(raw.get_value('elapsed'))
        self.assertEqual(elapsed, 0.001128531)

    def test_simple_exec(self):
        """LinuxPerf Test / Simple Exec"""
        date = LinuxPerf(['date'])
        date.stat()
        date.parse()

        inst = int(date.get_value('instructions'))
        self.assertTrue(inst > 10000)
        self.assertTrue(inst < 1000000)

        branches = int(date.get_value('branches'))
        self.assertTrue(branches > 10000)
        self.assertTrue(branches < 1000000)

        cpum = int(date.get_value('cpu-migrations'))
        self.assertTrue(cpum >= 0)
        self.assertTrue(cpum < 10)

    def test_reading_files(self):
        """LinuxPerf Test / Reading Files"""
        root = os.path.dirname(os.path.abspath(__file__)) + "/x86_64"
        for _, _, files in os.walk(root):
            for logfile in files:
                logfile = root + '/' + logfile
                perf = LinuxPerf()
                perf.set_raw(Path(logfile).read_text())
                perf.parse()

                inst = int(perf.get_value('instructions'))
                self.assertTrue(inst > 1000000000000)
                self.assertTrue(inst < 2000000000000)

                branches = int(perf.get_value('branches'))
                self.assertTrue(branches > 50000000000)
                self.assertTrue(branches < 90000000000)

                cpum = int(perf.get_value('cpu-migrations'))
                self.assertEqual(cpum, 0)

    def test_errors(self):
        """LinuxPerf Test / Errors"""
        ## PerfData
        pdata = PerfData()
        result = pdata.parse(['123 instructions', '321 cycles'])
        self.assertFalse(result)

        pdata.append(['123 instructions', '321 cycles'])
        self.assertFalse(pdata.ext)

        pdata.set_name(['123 instructions', '321 cycles'])
        self.assertFalse(pdata.name)

        ## LinuxPerf
        lperf = LinuxPerf()
        self.assertFalse(lperf.program)

        lperf.append_argument('foo')
        self.assertEqual(lperf.program, ['foo'])

        lperf.append_argument(['bar', 'baz'])
        self.assertEqual(lperf.program, ['foo', 'bar', 'baz'])

        lperf.set_raw('123 456 789')
        lperf.parse()
        self.assertFalse(lperf.get_value('instructions'))

        lperf.set_raw('123 instructions')
        lperf.parse()
        self.assertEqual(int(lperf.get_value('instructions')), 123)
        self.assertFalse(lperf.get_value('cycles'))

        self.assertTrue(lperf.get_raw())
        lperf.set_raw('')
        self.assertFalse(lperf.get_raw())

    def test_data(self):
        """Data test / Simple"""

        failed = False
        try:
            Data("data", "none")
        except ValueError:
            failed = True
        finally:
            self.assertTrue(failed)

        example = PerfData()
        example.parse(RAW)
        data1 = Data('data1', 'sep=-,none,outlier=1,cluster=1,fit=1')
        data1.add_log('run1', 'bench-compiler-option-cores.log', example)
        self.assertEqual(data1.name, 'data1')
        self.assertEqual(data1.sep, '-')
        self.assertEqual(data1.num_cat, 4)
        self.assertEqual(data1.num_logs, 1)
        self.assertEqual(data1.analyses[0], None)
        self.assertTrue(str(data1.analyses[1]).endswith('Outliers'))
        self.assertTrue(str(data1.analyses[2]).endswith('Clustering'))
        self.assertTrue(str(data1.analyses[3]).endswith('CurveFit'))

if __name__ == '__main__':
    unittest.main()
