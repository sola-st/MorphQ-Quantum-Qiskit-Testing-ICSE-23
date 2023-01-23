FROM ubuntu:22.04

WORKDIR /root/

# Install OS dependencies
# Many of these are for blender, where we got the full list from:
#   https://wiki.blender.org/wiki/Building_Blender/Linux/Ubuntu
RUN apt-get update && \
    apt-get install -y \
         wget \
         xz-utils \
         build-essential \
         git subversion \
         cmake \
         libx11-dev \
         libxxf86vm-dev \
         libxcursor-dev \
         libxi-dev \
         libxrandr-dev \
         libxinerama-dev \
         libegl-dev && \
    apt-get clean



# Download and install Anaconda
RUN wget https://repo.anaconda.com/archive/Anaconda3-2022.10-Linux-x86_64.sh -O Anaconda3-2022.10-Linux-x86_64.sh
RUN bash Anaconda3-2022.10-Linux-x86_64.sh -b
RUN rm Anaconda3-2022.10-Linux-x86_64.sh

ENV PATH=/root/anaconda3/bin:$PATH

# Install unzip
RUN apt-get install unzip

# Move to the opt directory
WORKDIR /opt/

# Download the environment.yml file
RUN wget https://raw.githubusercontent.com/sola-st/MorphQ-Quantum-Qiskit-Testing-ICSE-23/main/environment.yml

# Install Python dependencies
RUN conda env create -f environment.yml

# Initialize the bash
RUN conda init bash

# Create data directory
RUN mkdir data

# Download Data
RUN wget -O data/figshare_data --no-check-certificate https://ndownloader.figshare.com/files/38923367/2

# Unzip Data
RUN unzip data/figshare_data -d data/
RUN mv data/morphq_evaluation_compressed/qmt_v52 data/qmt_v52
RUN mv data/morphq_evaluation_compressed/qmt_v53 data/qmt_v53


# Initialize the sh
RUN conda init bash
# activate MorphQ environment
RUN /bin/bash -c conda activate MorphQ

# Copy MorphQ files
COPY . /opt/

SHELL ["/bin/bash","-c"]
RUN conda init
RUN echo 'conda activate MorphQ' >> ~/.bashrc

# Run the container and open jupyter notebook
EXPOSE 8888
# start bash
CMD ["/bin/bash"]