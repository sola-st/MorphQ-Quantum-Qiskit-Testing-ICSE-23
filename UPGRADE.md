# Upgrade Guide

## Create a new Conda environment

Create a new Conda environment and install the latest Qiskit version.

```bash
conda create -n MorphQ-v1-2-4 python=3.10 -y && conda activate MorphQ-v1-2-4
# install the latest Qiskit version
pip install qiskit==1.2.1 qiskit-aer==0.15.1 qiskit-ibm-runtime==0.29.1

# install some common packages used in the tool
pip install click termcolor pyyaml pandas coverage matplotlib seaborn
pip install astunparse networkx Deprecated tqdm pytest astpretty

# export the requirements
pip list --format=freeze > requirements.txt
```

## Try Running The Generation

```bash
python3 -m lib.generate_new_config --version 01
```