Based on the script from this tutorial:
https://barro.github.io/2018/01/taking-a-look-at-python-afl/

Tool needed: clone AFL in a folder called `AFL` with the command:
```bash
git clone https://github.com/google/AFL.git
```
Install the python wrapper via pip (when in the conda environment):
```bash
pip install python-afl
```

The steps to run AFL are:
1. create a `fuzzable_module.py` file which contains the `fuzz_one`. Note that this function must raise an exception when there is a crash. The function must get the input via standard input (`stdin`) and raise an exception when crashing.
1. create a `fuzz.py` program which calls the AFL python library and calls the `fuzz_one` function multiple times. Note that it has a specific structure as explained in the tutorial such as the presence of `with afl.loop(N)` and `os._exit(0)`.
1. Note that the AFL has been cloned and compiled with `make` to create the executable files, then the folder path has been added to the `PATH` environment variable: `export PATH=$PATH:absolute_path_to_afl_folder`.
1. Put examples of inputs that you want to give to the `fuzz_one` function via standard input.
1. Now everything is ready. Run the fuzzer via command line when you are in the current folder:
```bash
AFL_SKIP_CPUFREQ=1 py-afl-fuzz -S simple-1 -m 200 -i input/ -o output/ -- python3 fuzz.py
```
where `-m` decides the memory limit and `-S` is the name of the subfolder in the output main folder.
1. You will see your output in the `output` folder.


**Warning**: sometime the encoding of the input (systin) needs to be converted, in our case it works using the command of Python 2 (apparently): `stdin_compat = sys.stdin`.


# Parallelization
Each command line run launch a single thread, follow this suggestion (https://github.com/google/AFL/blob/master/docs/parallel_fuzzing.txt). it consists in running the same command multiple times with a different flag, so that one thread is the master and the others are the slaves, but all are getting examples from the same folder: