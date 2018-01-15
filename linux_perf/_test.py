#!/usr/bin/env python3

"""Testing script for linux_perf functionality"""

from linux_perf import LinuxPerf

def _test_simple():
    print("Test Simple: ", end='')
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

# Tests
_test_simple()
