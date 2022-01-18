""""
This file contains the analyzer objects to plot and inspect the results.
"""


from sklearn.metrics import RocCurveDisplay
# import libraries
import seaborn as sns
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

import os
import pandas as pd
from copy import deepcopy

from utils import iterate_over, iterate_parallel


class Explorer(object):

    def load_all(self, experiment_path, benchmarks):
        # load program info data
        self.load_program_data(experiment_path, benchmarks)
        # load execution info data
        self.load_execution_data(experiment_path, benchmarks)
        # load ground truth data
        self.load_ground_truth_data(experiment_path, benchmarks)
        # load ALL detectors data
        self.load_detection_data(experiment_path, benchmarks)

    def focus_on_detector(self, detector_name):
        """Analyze only the specific detector data."""
        self.df_backup_original = deepcopy(self.df_all)
        self.detector_name = detector_name
        self.df_all = self.df_backup_original[
            self.df_backup_original["test"] == detector_name]

    # DATA LOADING - READ FOLDERS AND CREATE PANDAS DATAFRAMES

    def load_program_data(self, experiment_path, benchmarks):
        """Load the program data for the given benchmarks."""
        all_program_info = []
        for benchmark in benchmarks:
            print(f"BENCHMARK: {benchmark['name']} - PROGRAM INFO - reading ...  ")
            compiler_names = list(sorted([
                compiler['name']for compiler in benchmark['compilers']
            ]))
            folder = os.path.join(experiment_path, benchmark["name"], "programs", compiler_names[0])
            # folder = os.path.join(experiment_path, benchmark['name'], "original_programs")
            subfolders = [
                subfolder
                for subfolder in os.listdir(folder)
                if os.path.isdir(os.path.join(folder, subfolder))
            ]
            if len(subfolders) == 2:
                raise NotImplementedError("Need to support data from two different folders.")
            current_program_info = list(
                iterate_over(folder, ".json", parse_json=True))
            records_program_info = [
                {
                    "n_qubits": program["n_qubits"],
                    "circuit_id": program["circuit_id"],
                    "benchmark_name": program["benchmark_name"],
                    "strategy_a": program["strategy_program_generation"],
                    "strategy_b": None
                }
                for _, program in current_program_info
            ]
            all_program_info.extend(records_program_info)
        self.df_program_info = pd.DataFrame.from_records(all_program_info)

    def load_execution_data(self, experiment_path, benchmarks):
        """Load the execution data for the given benchmarks."""
        execution_info = []
        for benchmark in benchmarks:
            print(f"BENCHMARK: {benchmark['name']} - EXECUTION INFO - reading ...  ")
            compiler_names = list(sorted([
                compiler['name']for compiler in benchmark['compilers']
            ]))

            folder_a = os.path.join(experiment_path, benchmark["name"], "executions", compiler_names[0])
            folder_b = os.path.join(experiment_path, benchmark["name"], "executions", compiler_names[1])
            pairs_execution_info = list(
                iterate_parallel(folder_a, folder_b, ".json", parse_json=True))
            records_execution_info = [
                {
                    "circuit_id": circuit_id.split("_")[0]
                    if "_" in circuit_id else circuit_id,
                    "circuit_id_execution_level": circuit_id,
                    "benchmark_name": benchmark["name"],
                    "execution_a": res_a,
                    "execution_b": res_b,
                }
                for circuit_id, res_a, res_b in pairs_execution_info
            ]
            execution_info.extend(records_execution_info)
        self.df_execution_info = pd.DataFrame.from_records(execution_info)

    def load_ground_truth_data(self, experiment_path, benchmarks):
        """Load the ground truth data for the given benchmarks."""
        ground_truth = []
        for benchmark in benchmarks:
            print(f"BENCHMARK: {benchmark['name']} - GROUND TRUTH - reading ...  ")
            ground_truth_folder = os.path.join(experiment_path, benchmark["name"], "ground_truth")
            _, records_ground_truth = zip(*list(
                iterate_over(ground_truth_folder, ".json", parse_json=True)))
            # print(records_ground_truth)
            ground_truth.extend(records_ground_truth)
        self.df_ground_truth = pd.DataFrame.from_records(ground_truth)

    def load_detection_data(self, experiment_path, benchmarks):
        detector_data = []

        for benchmark in benchmarks:
            prediction_folder = os.path.join(
                experiment_path, benchmark["name"], "predictions")
            detector_specific_subfolders = [
                os.path.join(prediction_folder, subfolder)
                for subfolder in os.listdir(prediction_folder)
                if os.path.isdir(os.path.join(prediction_folder, subfolder))
            ]
            for detector_folder in detector_specific_subfolders:
                print(f"BENCHMARK: {benchmark['name']} - DETECTOR: {detector_folder} - reading ...  ")

                for filename, detector_res in iterate_over(detector_folder, filetype=".json", parse_json=True):
                    print(f"Reading: {filename}")
                    # remove the comparison
                    pairs = detector_res.pop('comparisons', None)

                    for pair in pairs:
                        new_record = {**pair, **detector_res}
                        detector_data.append(new_record)

        df_detector_results = pd.DataFrame.from_records(detector_data)
        df_grouped = df_detector_results.groupby(by=[
            "circuit_id", "comparison_name", "test", "platform_a", "platform_b", "path_exec_a", "path_exec_b"
        ]).median().sort_values(by="p_value").reset_index()
        df_grouped.rename(columns={"comparison_name":"benchmark_name"}, inplace=True)
        self.df_detector = df_grouped

    # INITIALIZE OBJECT
    def __init__(self, config):
        benchmarks = [
            comparison
            for comparison in config["comparisons"]
            if comparison.get("is_benchmark", False)
        ]
        self.load_all(config["experiment_folder"], benchmarks)

        # derive the column label form the ground truth
        self.df_ground_truth = self._create_label(self.df_ground_truth)
        # derive the output size
        self.df_execution_info = self._measure_output_size(self.df_execution_info)

        self.df_all = pd.merge(self.df_detector, self.df_ground_truth, on=["circuit_id", "benchmark_name"])
        self.df_all = pd.merge(self.df_all, self.df_program_info, on=["circuit_id", "benchmark_name"])
        self.df_all = pd.merge(self.df_all, self.df_execution_info, on=["circuit_id", "benchmark_name"])
        # measure coverage (relative output size)
        self.df_all = self._measure_output_coverage(self.df_all)

    # START SECTION: internal manipulation to enrich with new columns

    def _create_label(self, df_ground_truth):
        df_ground_truth["label"] = df_ground_truth["expected_divergence"].apply(
            lambda e: 1 if e else 0)
        return df_ground_truth

    def _measure_output_size(self, df_execution_info):
        df_execution_info["output_size_a"] = df_execution_info["execution_a"].apply(
            lambda e: len(e))
        df_execution_info["output_size_b"] = df_execution_info["execution_b"].apply(
            lambda e: len(e))
        return df_execution_info

    def _measure_output_coverage(self, df_all):
        df_all["output_size_total"] = df_all["n_qubits"].apply(
            lambda e: 2**e)
        df_all["output_coverage_a"] = df_all.apply(
            lambda row: round(row["output_size_a"] / row["output_size_total"], 6), axis=1
        )
        df_all["output_coverage_b"] = df_all.apply(
            lambda row: round(row["output_size_a"] / row["output_size_total"], 6), axis=1
        )
        return df_all

     # END SECTION

    def plot_ROC(self, prediction_column="p_value"):
        RocCurveDisplay.from_predictions(self.df_all["label"], self.df_all[prediction_column])

    def classify_based_on_pvalue(self, treshold=0.05):
        self.df_all["prediction_divergence"] = self.df_all["p_value"].apply(lambda e: e < treshold)
        self.df_all["correct_prediction"] = self.df_all.apply(
            lambda row: row["prediction_divergence"] == row["expected_divergence"],
            axis=1
        )

    def plot_benchmark_categories(self):

        df = self.df_all

        # set the figure size
        fig, ax = plt.subplots(figsize=(7, 3))

        # from raw value to percentage
        total = df.groupby('benchmark_name')['correct_prediction'].count().reset_index()
        correct = df[df["correct_prediction"]].groupby('benchmark_name')['correct_prediction'].count().reset_index()

        difference = set(total["benchmark_name"]).difference(set(correct["benchmark_name"]))
        if len(difference) > 0:
            for missing_bench in list(difference):
                new_row = {'benchmark_name':missing_bench, 'correct_prediction':0, 'samples':0}
                #append row to the dataframe
                correct = correct.append(new_row, ignore_index=True)

        correct['samples'] = [i / j * 100 for i,j in zip(correct['correct_prediction'], total['correct_prediction'])]
        total['samples'] = [i / j * 100 for i,j in zip(total['correct_prediction'], total['correct_prediction'])]

        # bar chart 1 -> top bars (group of 'smoker=No')
        sns.barplot(y="benchmark_name",  x="samples", data=total, color='orange', ax=ax)


        # bar chart 2 -> bottom bars (group of 'smoker=Yes')
        sns.barplot(y="benchmark_name", x="samples", data=correct, color='blue', ax=ax)

        # add legend
        top_bar = mpatches.Patch(color='orange', label='Wrong predictions')
        bottom_bar = mpatches.Patch(color='blue', label='Correct predictions')
        fig.legend(handles=[top_bar, bottom_bar])

        ax.set_xlabel("% of samples")
        ax.set_ylabel("Benchmark Name")
        ax.set_xlim(0,100)
        ax.set_title(f"Test: {self.detector_name}")

        # show the graph
        fig.show()

    def inspect_mispredictions(self, variable_to_inspect="n_qubits", benchmark_name=None):
        mispredictions = self.df_all[~self.df_all["correct_prediction"]]
        self.inspect(variable_to_inspect, benchmark_name, mispredictions, "Mispredictions")

    def inspect(self, variable_to_inspect="n_qubits", benchmark_name=None, df=None, title=None):
        if df is None:
            df = self.df_all
        if benchmark_name is not None:
            if isinstance(benchmark_name, list):
                df = df[df["benchmark_name"].isin(benchmark_name)]
            else:
                df = df[df["benchmark_name"] == benchmark_name]
        df[variable_to_inspect] = np.around(df[variable_to_inspect], decimals=6)
        tot = len(self.df_all)
        try:
            ax = sns.histplot(data=df, x=variable_to_inspect)
            if title is None:
                ax.set_title(f"{len(df)}/{tot} - {benchmark_name}")
            else:
                ax.set_title(title)
        except ValueError:
            print("Scale of the data was too small or too big to plot.")
            print("Raw data: ", sorted(df[variable_to_inspect]))
        print(f"We have displayed {len(df)}/{tot} datapoints.")
        print(f"[resticted to: {benchmark_name}")

    def get_mispredictions(self):
        return self.df_all[~self.df_all["correct_prediction"]]