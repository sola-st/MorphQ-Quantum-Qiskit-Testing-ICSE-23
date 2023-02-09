
## Docker Setup

We also provide a Dockerfile to run MorphQ in a Docker container.

1. To build the Docker image, run the following command:
    ```bash
    docker build -t morphq .
    ```
1. To run the Docker container, run the following command:
    ```bash
    docker run -it --rm -p 8888:8888 morphq
    ```

Optionally: To avoid the build process, you can also use the ready made Docker image from Docker Hub:
```bash
docker run -it --rm -p 8888:8888 mattepalte/morphq:latest
```

### LEVEL 1: Reproduce the Paper Figures

1. To run the notebook in the Docker container, run the following command:
    ```bash
    jupyter notebook --allow-root --no-browser --ip=0.0.0.0 --port=8888
    ```
1. Then open the link that is printed in the terminal in your browser. Note that the link will look something like this: `http://127.0.0.1:8888/?token=6819f647f19859d9e92013a41f52f49d6ffed633e7b68657`.
1. Open the `notebooks/RQs_Reproduce_Analysis_Results_Level_1.ipynb` notebook.
1. Run the notebook top-to-bottom.
1. Congratulations! You reproduced all the paper figures based on our experimental data.


### LEVEL 2: Run MorphQ For a New Testing Campaign

1. Generate a new configuration file with the following command:
    ```bash
    python3 -m lib.generate_new_config --version 01
    ```
1. Select `morphq_demo.yaml` as the base configuration file.
1. Run the following command to run MorphQ with the new configuration:
    ```bash
    python3 -m lib.qmt config/qmt_v01.yaml
    ```
1. Congratulations! You successfully run MorphQ.

**Persisting Data**

Note that your newly generated data will be transient in this Docker, thus if you are interested in accessing them need to mount a folder on your host mahcine (aka laptop) as a volume in the docker container.

Follow these steps, while in the root folder of the cloned repository:
1. Create a data folder to store all the docker generated data:
    ```bash
    mkdir data_docker
    ```
2. Run the following command to run MorphQ with the new configuration (if you use another OS instead of Ubuntu, the syntax might be a little different, see this [link](https://stackoverflow.com/a/41489151)):
    ```bash
    docker run -it --rm -p 8888:8888 -v $(pwd)/data_docker:/opt/data mattepalte/morphq:latest
    ```
3. Run the steps in Level 2 above:
    ```bash
    python3 -m lib.generate_new_config --version 01 # select morphq_demo.yaml as the base configuration file
    python3 -m lib.qmt config/qmt_v01.yaml
    ```
4. When enough data is generated, stop MorphQ by pressing `Ctrl+C`, and type `exit` to exit the docker container.
4. You can now access the data in the `data_docker` folder on your laptop even when the docker is not running.
