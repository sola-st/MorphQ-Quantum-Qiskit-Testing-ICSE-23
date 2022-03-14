
Run this command from the `lib` directory.

## Metamorphic on Qiskit
To run the `Quantum Metamorphic Testing` test suite, use the following command:
```bash
screen -L -Logfile ../data/qmt_v0Y/log_fuzzy.txt -S qmt_v0Y python3 qmt.py ../config/qmt_v0Y.yaml
```

## Cross-Platform (Cirq and Qiskit)
To run the `cross-platform testing` use the following commands:
```bash
# for generation
screen -L -Logfile ../data/experiment_v0X/log_detect.txt -S exp_v0X python3  cross_platform_testing.py generate ../config/experiment_v0X.yaml
# for detection
screen -L -Logfile ../data/experiment_v0X/log_detect.txt -S exp_v0X python3  cross_platform_testing.py detect ../config/experiment_v0X.yaml
```

## Cross-Platform for benchmark
To run the `benchmark of detectors` use the following commands:
For generation only
```bash
# for generation
screen -L -Logfile ../data/experiment_v0X/log_detect.txt -S exp_v0X python3  cross_platform_testing.py generate --benchmark ../config/experiment_v0X.yaml
# for detection
screen -L -Logfile ../data/experiment_v0X/log_detect.txt -S exp_v0X python3  cross_platform_testing.py detect --benchmark ../config/experiment_v0X.yaml
```


## Troubleshooting
1. Are you running the commands from inside the `lib` directory.
1. Did you activate the conda environment? via `conda activate ML4Quantum`