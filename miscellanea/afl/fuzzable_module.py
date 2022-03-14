"""
This can be run with a following command after afl
<http://lcamtuf.coredump.cx/afl/> and python-afl
<https://github.com/jwilk/python-afl> have been installed:

    AFL_SKIP_CPUFREQ=1 py-afl-fuzz -S simple-1 -m 200 -i input/ -o output/ -- \
        /usr/bin/python target-python-simple.py

"""

import string
import sys

VALUES = {}
for value, char in enumerate(string.ascii_lowercase):
    VALUES[char] = value


def fuzz_one(stdin, values):
    data = stdin.read(128)
    total = 0
    for key in data:
        #print(key.encode("utf-8"))
        if key == 'a':
            raise Exception("This is a test")
        #if key.encode("utf-8") == 'b':
        #    raise Exception("This is another test")
        if key not in values:
            continue
        value = values[key]
        if value % 5 == 0:
            total += value * 5
            total += ord(key)
        elif value % 3 == 0:
            total += value * 3
            total += ord(key)
        elif value % 2 == 0:
            total += value * 2
            total += ord(key)
        else:
            total += value + ord(key)
    print(VALUES)
    print(total)


if __name__ == "__main__":
    fuzz_one(sys.stdin, VALUES)
