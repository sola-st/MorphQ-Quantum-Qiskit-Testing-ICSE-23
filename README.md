
# MorphQ Software

The MorphQ software is open source and you find all the relevant source files in the [lib](lib) folder.

You can run MorphQ with two objectives:
1. [Replication Package Level 1](#Reproduce-the-Paper-figures): reproduce paper's results.
2. [Replication Package Level 2](#Run-your-own-Testing-Campaigns): run new testing campaigns to find new bugs in Qiskit. or compare your new testing method against MorphQ. (Note: you can also use our method in the Qdiff configuration to compare against QDiff transformations.)

# Getting started

## Setup Environment

We provide the `environment.yml` file in the main folder to recreate the exact Conda environment with the same pip and Conda packages.
(Download Conda for your system [here](https://docs.conda.io/projects/conda/en/latest/user-guide/install/download.html))
Run the following command:
```bash
conda env create -f environment.yml
```
Then activate the environment with:
```bash
conda activate MorphQ
```

# Reproduce the Paper figures
**Replication Package Level 1**

This replication level allows other researcher to independently reproduce the results of our paper starting form the experimental data we collected during our empirical evaluation.

Follow this steps:
1. Download the datasets used in our evaluation section from this [link](https://figshare.com/s/dd0d4af20fd6e06148a3).

2. unzip the archive. Be patient since it might take some time, since they are 2GB of relatively small files.

3. copy the folders `qmt_v52` and `qmt_v53` in the `data` directory.

4. to open jupyter notebook, run the following in your terminal:
    ```bash
    conda activate MorphQ
    jupyter notebook
    ```

5. In the jupyter notebook web interface, navigate to and execute top-to-bottom the following notebook: [notebooks/RQs_Reproduce_Analysis_Results.ipynb](notebooks/RQs_Reproduce_Analysis_Results.ipynb).

## Inspect the Warnings found during our Empirical Evaluation
To see the warnings described in our empirical evaluation of the paper refer to the [`warnings/program_pairs`](warnings/program_pairs) folder.
There you will find a subfolder for each program pairs which contains:
- the source quantum program: `source.py`
- the follow-up quantum program generated via metamorphic transformations: `follow-up.py`
- the metadata of the generation of the program pair: `metadata.json`
- the metadata of the execution of the program pair: `metadata_exec.json`
- an anonymized screenshot of the issue page: `program_code.pdf`


# Run your own Testing Campaigns
**Replication Package Level 2**

This guide is intended for researchers who want to: (1) run their own testing campaigns to find new bugs in Qiskit with MorphQ, (2) compare MorphQ with a novel automatic testing approach of the Qiskit platform.

A MorphQ run is configured via a YAML file, read next to learn how to configure your own run. The one used for our experiment are store in the [config](config) folder:
- [qmt_v53.yaml](config/qmt_v53.yaml): configuration file used for our experiment for the actual **MorphQ**.
- [qmt_v52.yaml](config/qmt_v52.yaml): configuration file used for our experiment for the **QDiff-Transformations**.

Some important fields in the config file are:
- `experiment_folder`: the folder where the data will be stored.
- `generation_strategy`: the strategy to use to generate the source quantum programs. You can tweak the parameters to define their size: `min_n_qubits`, `max_n_qubits`, `min_n_ops`, `max_n_ops`; and the basic gates used: `gate_set`. Note: in case you want to change the program generator at all, you can simply plug a different object in the `generator_object` field, remember to use the same interface of the `QiskitFuzzer` class in the [lib/generation_strategy_python.py](/lib/generation_strategy_python.py) file.
- `max_transformations_per_program`: the max number of metamorphic transformations to apply to each program in a chain.
- `transformation_mode`: the metamorphic transformation to apply, either `morphq` or `qdiff`.
- `morphq_metamorphic_strategies`: the metamorphic transformation to apply for the `morphq` mode.
- `qdiff_metamorphic_strategies`: the metamorphic transformation to apply for the `qdiff` mode.
- `coverage_settings_filepath`: the  path to the coverage settings, typically a `.cover` file. You can find some examples in the [config](config) folder.


## Run MorphQ

We prepared a convenient way to generate a new configuration file from a template.

1. run the following command:
    ```bash
    python3 -m lib.generate_new_config --version 01
    ```
2. type the number to select the `morphq_demo.yaml` template. You should get the following output:
    ```python3 -m lib.generate_new_config --version 01
    Available Templates:
    1. morphq_demo.yaml
    2. morphq.yaml
    3. qdiff_demo.yaml
    4. qdiff.yaml
    Choose a template: 1
    Setting file created: ./config/qmt_v01.yaml

    Creating coverage file:
    Coverage file created:: config/qmt_v01.cover

    Creating experiment folder:
    mkdir -p data/qmt_v01/
    Experiment folder created: data/qmt_v01/

    Excluding experiment folder from gitignore:
    echo 'data/qmt_v01/' >> .gitignore
    Added to .gitignore: data/qmt_v01/

    Example commands:

    - Simple experiment run (no monitoring):
    python3 -m lib.qmt config/qmt_v01.yaml

    - Experiment run (monitoring via screen):
    screen -L -Logfile data/qmt_v01/log_fuzzy.txt -S qmt_v01 python3 -m lib.qmt config/qmt_v01.yaml
    ```
3. The you can run the MorphQ, either without the monitoring or with the monitoring (using screen), as mentioned in the output.
    ```bash
    - Simple experiment run (no monitoring):
    python3 -m lib.qmt config/qmt_v01.yaml

    - Experiment run (monitoring via screen):
    screen -L -Logfile data/qmt_v01/log_fuzzy.txt -S qmt_v01 python3 -m lib.qmt config/qmt_v01.yaml
    ```
    Note: if you do not have screen installed, you can install it with `sudo apt install screen`.
4. If you used the monitoring setup, you will find the log at the specified path (e.g., `data/qmt_v01/log_fuzzy.txt`). And it should contain what you see in the terminal. An example is shown belowe:
    ```bash
    tarting loop... [no timer]
    Data file:  data/qmt_v01/coverage.db
    --------- New programs pair... [timer: 120 sec] (2023-01-17-13:25:56) ----------
    Applying: MetamorphicTransformation(ToQasmAndBack)
    Follow: add 'qc' conversion to and from QASM (before: EXECUTION)
    Applying: MetamorphicTransformation(ChangeTargetBasis)
    Follow: gateset replaced with:  ['ccx', 'h']
    Applying: MetamorphicTransformation(ChangeTargetBasis)
    Follow: gateset replaced with:  ['rx', 'ry', 'rz', 'p', 'cx']
    N. applied transformations:  3
    Executing: 381b90a6f912482f90076c971f2f7074 (2023-01-17-13:25:57)
    Exceptions from execution: {'source': None, 'followup': '"Cannot unroll the circuit to the given basis, [\'rx\', \'ry\', \'rz\', \'p\', \'cx\']. Instruction id not found in equivalence library and no rule found to expand."'}
    --------- New programs pair... [timer: 120 sec] (2023-01-17-13:25:57) ----------
    Applying: MetamorphicTransformation(ToQasmAndBack)
    Follow: add 'qc' conversion to and from QASM (before: OPTIMIZATION_LEVEL)
    Applying: MetamorphicTransformation(InjectParameters)
    Follow: from concrete values to parameters (12/18):{'p_a0b579': 0.14709460241864125, 'p_2d234e': 2.7426492410962213, 'p_4aca1b': 1.4655643254447606, 'p_45c5e7': 1.2941054775314977, 'p_079834': 1.297948790230138, 'p_7cd8ae': 4.883628121581527, 'p_afbea1': 5.665169039628415, 'p_761208': 1.8300494450884037, 'p_6baf69': 2.5947845640969898, 'p_098317': 4.818497722767661, 'p_134a27': 5.236334390147421, 'p_e21ca9': 3.219605809291016}
    Applying: MetamorphicTransformation(AddUnusedRegister)
    Follow: add QuantumRegister(1)
    N. applied transformations:  3
    Executing: f41d90fd3cb94e6f925f07c0a20e2a48 (2023-01-17-13:25:58)
    Exceptions from execution: {'source': None, 'followup': None}
    i*: 0
    --------- New programs pair... [timer: 120 sec] (2023-01-17-13:25:59) ----------
    Applying: MetamorphicTransformation(ChangeOptLevel)
    Follow: optimization level changed: 1 -> 0
    Applying: MetamorphicTransformation(ToQasmAndBack)
    Follow: add 'qc' conversion to and from QASM (before: EXECUTION)
    Applying: MetamorphicTransformation(ChangeOptLevel)
    Follow: optimization level changed: 0 -> 2
    Applying: MetamorphicTransformation(ChangeCouplingMap)
    Follow: coupling map changed: None -> [[0, 1], [1, 0], [1, 2], [2, 1]]
    N. applied transformations:  4
    Executing: 7e5582035ba3412eb8d8dba421cf6549 (2023-01-17-13:25:59)
    Exceptions from execution: {'source': None, 'followup': None}
    i*: 0
    ```
5. Congratulation! MorphQ is running!
6. If you want to stop the experiment, you can do it by pressing `Ctrl+C` in the terminal. If you used the monitoring setup, you can also do it by typing `screen -S qmt_v01 -X quit` in the terminal.

## Extra Utilities: Inspect Warnings of your run

Here we describe where to find and how to inspect the warnings generated by `MorphQ`.

The relevant warnings of your run will be stored in a the `qfl.db` sqlite database in the `data/qmt_vXX/` folder.
To inspect them use the notebook [`notebooks/Demo_Warnings_Manual_Inspection.ipynb`](notebooks/Demo_Warnings_Manual_Inspection.ipynb).
Remember to update the `EXP_FOLDER = "qmt_v53"` cell to point ot the actual `qmt_vXX` folder of your run.


## Extra Run: QDiff-Transformations

To run the QDiff pipeline, just pick a `qdiff` template when prompted by running:
```bash
python3 -m lib.generate_new_config --version 02
```


## Extra details: using your own settings
Before starting your test run, you need to prepare some configuration files in the data [`config`](config) folder.

1. create a `qmt_vXX.yaml` file in the `config` folder. On this file you can set almost all the parameters of the test. Including the metamorphic relationships to use (via the `metamorphic_strategies` field) and the program generation mechanism (via the `generation_strategy` field).

**IMPORTANT**: Remember to update the two field: `experiment_folder` to point to the data folder (e.g., `data/qmt_vXX/`) and `coverage_settings_filepath` to point to the file containing the coverage settings (e.g., `config/qmt_vXX.cover`).

2. create a `qmt_vXX.cover` file in the `config` folder. On this file you can set the coverage settings.

**IMPORTANT**: update the `data_file` field to specify the final name of the coverage database in the correct data folder (e.g., `data/qmt_vXX/.coverage`).

3. (optional) to avoid that the generated programs are processed by the git installation add the data folder to your `.gitignore` file.
```
data/qmt_vXX/*
```


# Troubleshooting
Some questions you might ask yourself are:
1. Did you install and activate the conda environment? via `conda activate MorphQ`

## Our Hardware Setup
We tested MorphQ with the following setups:

### Main Experiment
- Operating System: Ubuntu 18.04.6 LTS
- Linux version 4.15.0-167-generic
- Architecture: x86-64
- CPU: Intel(R) Xeon(R) Silver 4214 CPU @ 2.20GHz
- conda 4.11.0
- RAM: 252 GB

### Artifact Evaluation Setup
We also tested it on a Ubuntu 20.04 with 64 GB of RAM and 8 cores.