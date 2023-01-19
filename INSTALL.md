## Setup Environment

We provide the `environment.yml` file in the main folder to recreate the exact Conda environment with the same pip and Conda packages.


1. Clone this repository: `git clone https://github.com/sola-st/MorphQ-Quantum-Qiskit-Testing-ICSE-23.git`
2. make sure you have conda on your system (Download Conda for your system [here](https://docs.conda.io/projects/conda/en/latest/user-guide/install/download.html)) and that your system meets all the requirements (see [REQUIREMENTS.md](REQUIREMENTS.md))
3. Run the following command:
    ```bash
    conda env create -f environment.yml
    ```
4. Then activate the environment with:
    ```bash
    conda activate MorphQ
    ```
5. Congratulations! You are ready to run MorphQ.

