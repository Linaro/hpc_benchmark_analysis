#!/usr/bin/env python3

"""Testing script for linux_perf functionality"""

import os
from pathlib import Path
from linux_perf import LinuxPerf, PerfData

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

def _test_raw():
    print("LinuxPerf Test / Raw: ", end='')
    raw = LinuxPerf()
    raw.set_raw(RAW)
    raw.parse()

    inst = int(raw.get_value('instructions'))
    assert inst == 300826, 'Wrong number of instructions'

    branches = int(raw.get_value('branches'))
    assert branches == 65455, 'Wrong number of branches'

    elapsed = float(raw.get_value('elapsed'))
    assert elapsed == 0.001128531, 'Wrong elapsed time'

    print("PASS")

def _test_simple_exec():
    print("LinuxPerf Test / Simple Exec: ", end='')
    date = LinuxPerf(['date'])
    date.stat()
    date.parse()

    inst = int(date.get_value('instructions'))
    assert inst > 10000, 'Number of instructions too low'
    assert inst < 1000000, 'Number of instructions too high'

    branches = int(date.get_value('branches'))
    assert branches > 10000, 'Number of branches too low'
    assert branches < 1000000, 'Number of branches too high'

    cpum = int(date.get_value('cpu-migrations'))
    assert cpum >= 0, 'Number of instructions too low'
    assert cpum < 10, 'Number of instructions too high'

    print("PASS")

def _test_reading_files():
    print("LinuxPerf Test / Reading Files: ", end='')
    root = os.path.dirname(os.path.abspath(__file__)) + "/x86_64"
    for _, _, files in os.walk(root):
        for logfile in files:
            logfile = root + '/' + logfile
            perf = LinuxPerf()
            perf.set_raw(Path(logfile).read_text())
            perf.parse()

            inst = int(perf.get_value('instructions'))
            assert inst > 1000000000000, 'Number of instructions too low'
            assert inst < 2000000000000, 'Number of instructions too high'

            branches = int(perf.get_value('branches'))
            assert branches > 50000000000, 'Number of branches too low'
            assert branches < 90000000000, 'Number of branches too high'

            cpum = int(perf.get_value('cpu-migrations'))
            assert cpum == 0, 'Wrong number of instructions'

    print("PASS")

def _test_errors():
    print("LinuxPerf Test / Errors: ", end='')
    ## PerfData
    pdata = PerfData()
    result = pdata.parse(['123 instructions', '321 cycles'])
    assert not result, "Shouldn't have parsed list"

    pdata.append(['123 instructions', '321 cycles'])
    assert not pdata.ext, "Shouldn't have appended list"

    pdata.set_name(['123 instructions', '321 cycles'])
    assert not pdata.name, "Shouldn't have used list as name"

    ## LinuxPerf
    lperf = LinuxPerf()
    assert not lperf.program, "Default program should be empty"

    lperf.append_argument('foo')
    assert lperf.program == ['foo'], "New argument should be 'foo'"

    lperf.append_argument(['bar', 'baz'])
    assert lperf.program == ['foo', 'bar', 'baz'], "Full argument should be 'foo', 'bar', 'baz'"

    lperf.set_raw('123 456 789')
    lperf.parse()
    assert not lperf.get_value('instructions'), "Bad input shouldn't parse nor fail"

    lperf.set_raw('123 instructions')
    lperf.parse()
    assert int(lperf.get_value('instructions')) == 123, "Should have had instructions"
    assert not lperf.get_value('cycles'), "Should not have had cycles"

    assert lperf.get_raw(), "Should have some raw data"
    lperf.set_raw('')
    assert not lperf.get_raw(), "Should have cleared raw data"

    print("PASS")

# Tests
_test_raw()
_test_simple_exec()
_test_reading_files()
_test_errors()
