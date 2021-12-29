"""
This can be run with a following command after afl
<http://lcamtuf.coredump.cx/afl/> and python-afl
<https://github.com/jwilk/python-afl> have been installed:

    AFL_SKIP_CPUFREQ=1 py-afl-fuzz -S simple-1 -m 200 -i input/ -o output/ -- \
        /usr/bin/python target-python-simple.py

"""

import afl
from fuzzable_module import fuzz_one
import os
import sys
import string

stdin_compat = sys.stdin


try:  # type-loop-seek
    stdin_compat.seek(0)  # type-loop-seek

    def seek_stdin():  # type-loop-seek
        stdin_compat.seek(0)  # type-loop-seek
except (IOError, OSError):  # type-loop-seek
    def seek_stdin():  # type-loop-seek
        pass  # type-loop-seek


VALUES = {}
for value, char in enumerate(string.ascii_lowercase):
    VALUES[char] = value


#afl.init()  # type-post-imports type-os-exit
#fuzz_one(stdin_compat, VALUES)  # type-os-exit
while afl.loop(100):  # type-afl-loop type-loop-seek
    seek_stdin()  # type-loop-seek
    fuzz_one(stdin_compat, VALUES)  # type-afl-loop type-loop-seek
os._exit(0)  # type-afl-loop type-os-exit