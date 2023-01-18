# Requirements

The following requirements are needed to run the code in this repository:
1. O.S.:Recommended: Ubuntu 18.04 LTS or Ubuntu 20.04 LTS. *It should work with other systems but we cannot guarantee that.*
1. RAM: we tested on system with at least 64 GB of RAM. *If you reduce the size of the quantum programs to generate, you should be able to reduce the RAM requirements, but we cannot guarantee that.*
1. Package and environment manager: Conda [download here](https://docs.conda.io/projects/conda/en/latest/user-guide/install/download.html))
1. Clone this repository: `git clone git clone https://github.com/sola-st/MorphQ-Quantum-Qiskit-Testing-ICSE-23.git`
1. Download the experimental data [here](https://doi.org/10.6084/m9.figshare.20703091.v1). Unzip them in the `data` folder. It might take time since the archive contains many small files.
1. Optional: screen (to run the experiments in the background). Get via `sudo apt install screen`.


## Our Hardware Setup
We tested MorphQ with the following setups:

**Main Experiment**
- Operating System: Ubuntu 18.04.6 LTS
- Linux version 4.15.0-167-generic
- Architecture: x86-64
- CPU: Intel(R) Xeon(R) Silver 4214 CPU @ 2.20GHz
- conda 4.11.0
- RAM: 252 GB

**Artifact Evaluation Setup**
We also tested it on a Ubuntu 20.04 with 64 GB of RAM and 8 cores.