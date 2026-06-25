# Upgrade Guide

## Create a new Conda environment

Create a new Conda environment and install the latest Qiskit version.

```bash
conda create -n MorphQ-v1-2-4 python=3.10 -y && conda activate MorphQ-v1-2-4
# install the latest Qiskit version
pip install qiskit==1.2.4 qiskit-aer==0.15.1 qiskit-ibm-runtime==0.29.0

# install some common packages used in the tool
pip install click termcolor pyyaml pandas coverage matplotlib seaborn
pip install astunparse networkx Deprecated tqdm pytest astpretty

# export the requirements
pip list --format=freeze > requirements.txt
```

## Try Running The Generation

```bash
python3 -m lib.generate_new_config --version 01

# run the fuzzing
python3 -m lib.qmt config/qmt_v12.yaml

# create the xml report
cd data/qmt_v12
coverage xml
```

# Coverage with Rust

base image:
```bash
docker run -it --rm qiskit_w_rust /bin/bash
```


```bash
# run docker with the mounting:
# ---
# pwd:data >> /home/regularuser/qiskit/data
# pwd:config >> /home/regularuser/qiskit/config
# ---
# pwd:lib >> /home/regularuser/app/lib
# pwd:pyproject.toml >> /home/regularuser/app/pyproject.toml

cd MorphQ-Quantum-Qiskit-Testing-ICSE-23/

# FROM REPO ROOT
docker run -it --rm -v $(pwd)/data:/home/regularuser/qiskit/data -v $(pwd)/config:/home/regularuser/qiskit/config -v $(pwd)/lib:/home/regularuser/app/lib -v $(pwd)/pyproject.toml:/home/regularuser/app/pyproject.toml qiskit_w_rust /bin/bash

# inside the docker
cd /home/regularuser/app
pip install -e .
cd /home/regularuser/qiskit
python3 -m lib.generate_new_config --version 14

# run the fuzzing
python3 -m lib.qmt config/qmt_v14.yaml

# collect coverage from rust
llvm-profdata merge -sparse qiskit-*.profraw -o my_program.profdata && \
llvm-cov export -Xdemangler=rustfilt target/debug/libqiskit_pyext.so --instr-profile=my_program.profdata --format=lcov --ignore-filename-regex='^(?!crates).*$' > coverage.lcov && \
lcov_cobertura -e '^(?!crates).*$' coverage.lcov -o rust_coverage.xml
# copy the rust_coverage.xml to the host
cp rust_coverage.xml /home/regularuser/qiskit/data/qmt_v14

# # create the xml report for python
# cd /home/regularuser/qiskit/data/qmt_v14
# coverage xml

# create the xml report for python
cd /home/regularuser/qiskit/
# open the config/qmt_v14.cover and update the paths
# replacing `/home/regularuser/qiskit/qiskit` with `qiskit`
sed -i 's|/home/regularuser/qiskit/qiskit|qiskit|g' /home/regularuser/qiskit/config/qmt_v14.cover

coverage xml --data-file=/home/regularuser/qiskit/data/qmt_v14/.coverage  --rcfile=/home/regularuser/qiskit/config/qmt_v14.cover -o /home/regularuser/qiskit/data/qmt_v14/coverage.xml

```

## Create a new Conda environment for Qiskit 2.3.0 with QASM 3

To run MorphQ with Qiskit 2.3.0 and QASM 3:
```
source /home/ubuntu/miniconda3/etc/profile.d/conda.sh
conda --version
conda create -n MorphQ-v2-3-0 python=3.10 -y
conda activate MorphQ-v2-3-0
pip install -e .
pip install -r requirements-QASM3.txt
python3 -m lib.qmt config/qmt_v54q3.yaml
```
