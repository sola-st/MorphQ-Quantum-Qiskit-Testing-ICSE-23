"""
This file inspects a specific divergent comparison to find the root cause.
"""


# import libraries
from pydoc import plain
import seaborn as sns
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches


from typing import List, Tuple, Dict, Any

import os
import pandas as pd
from utils import load_json, load_multiple_json


class Inspector(object):

    def __init__(self,
                 folder_executions: str,
                 platform_names: Tuple[str, str] = ["qiskit", "cirq"]) -> None:
        super().__init__()
        self.folder_executions = folder_executions
        self.platform_names = platform_names

    def inspect(self,
                df: pd.DataFrame,
                divergent_id: int,
                colname_pvalue: str,
                colname_id: str = "program_id") -> None:
        """Select a program form a dataframe and load the results."""
        df[colname_id] = df[colname_id].astype(int)
        df_to_inspect = df[df[colname_id] == divergent_id]
        if len(df_to_inspect) > 1:
            print(f"There are {len(df_to_inspect)} records for program: {divergent_id}")
        divergent_record = df_to_inspect.iloc[0]
        self.p_value = divergent_record[colname_pvalue]
        self.p1_results, self.p2_results = [
            self.get_results(
                divergent_id=divergent_id,
                platform_name=platform_name)
            for platform_name in self.platform_names
        ]
        self._create_dataframes()

    def _create_dataframes(self):
        p1_strings, p1_counters = list(zip(*list(self.p1_results.items())))
        p1_names = [f"{self.platform_names[0]}"
                    for _ in range(len(p1_strings))]
        p2_strings, p2_counters = list(zip(*list(self.p2_results.items())))
        p2_names = [f"{self.platform_names[1]}"
                    for _ in range(len(p2_strings))]
        all_strings = p1_strings + p2_strings
        all_counters = p1_counters + p2_counters
        all_names = p1_names + p2_names

        df = pd.DataFrame(zip(all_strings, all_counters, all_names), columns=["string", "counter", "name"])
        df = df.sort_values(by=["counter"], ascending=False)
        self.df_melted = df
        self.df_p1 = df[df["name"] == f"{self.platform_names[0]}"]
        self.df_p2 = df[df["name"] == f"{self.platform_names[1]}"]
        self.df_joined = pd.merge(self.df_p1, self.df_p2, on="string")

    def get_results(self, divergent_id, platform_name):
        """Read the results for the program with this id and platform name."""
        path_platform = os.path.join(
            self.folder_executions, platform_name
        )
        all_executions = os.listdir(path_platform)
        if f"{divergent_id}.json" in all_executions:
            return load_json(
                filename=f"{divergent_id}.json", folder=path_platform)
        elif f"{divergent_id}_0.json" in all_executions:
            return load_multiple_json(
                program_id=divergent_id, folder=path_platform)
        else:
            return {}

    def plot_execution_top_k(self, k=10, confidence_level=0.95):
        """Print histogram results of the two distributions."""
        self._plot_result_single_platform(
            self.p1_results, platform_name=self.platform_names[0],
            top_k=k, confidence_level=confidence_level)
        self._plot_result_single_platform(
            self.p2_results, platform_name=self.platform_names[1],
            top_k=k, confidence_level=confidence_level)

    def plot_histogram_together(self, top_perc=.25, figsize=(10, 6)):
        """Plot the histogram together for both platforms.

        Note that the top_perc is the percentage of the top solutions to plot.
        """
        df = self.df_melted
        df = self._cap_top_perc(df, top_perc)
        plt.figure(figsize=figsize)
        sns.barplot(x="string", hue="name", y="counter", data=df)
        # rotate labels 90
        plt.xticks(rotation=90)
        plt.show()

    def _plot_result_single_platform(self, execution_dict, platform_name,
                                     top_k=10, confidence_level=0.95):
        """Print results single execution."""
        pairs_solution_frequency = list(execution_dict.items())
        occurrences = [e[1] for e in pairs_solution_frequency]
        total = sum(occurrences)
        max_value = max(occurrences)
        n_qubits = len(pairs_solution_frequency[0][0])
        expected_uniform_occurency = (float(1)/2**n_qubits) * 100
        if len(pairs_solution_frequency) > top_k:
            pairs_solution_frequency = sorted(pairs_solution_frequency, key=lambda x: x[1], reverse=True)[:top_k]
        else:
            pairs_solution_frequency = sorted(pairs_solution_frequency)
        strings, occurrences = list(zip(*pairs_solution_frequency))
        error = self._compute_error_bars(occurrences, total, confidence_level)
        plt.bar(x=range(len(strings)), height=occurrences,
                tick_label=strings, yerr=error, align='center', alpha=0.5, ecolor='black', capsize=10)
        plt.xticks(rotation=90)
        plt.title(f"{platform_name} (n_qubits: {n_qubits})")
        for i, (k, v) in enumerate(pairs_solution_frequency):
            perc = ((float(v) / total) * 100)
            plt.text(i, max_value / 5, f"{perc:.1f}%", color='black', fontweight='bold', rotation=90)
        plt.text(int(top_k/2), max_value * .8,
                 f"Uniform threshold: {expected_uniform_occurency:.1f}%",
                 color='black', fontweight='bold')
        plt.hlines(expected_uniform_occurency * total / 100, -1, top_k, colors='red')

        plt.show()

    def _compute_error_bars(self, y, n_shots, confidence_level=0.95):
        """Compute the error bars for the histogram."""
        prob_y = [float(e/n_shots) for e in y]
        err = [
           confidence_level * np.sqrt(prob_y[i] * (1 - prob_y[i]) / n_shots)
           for i in range(len(y))
        ]
        scaled_up_error = [e * n_shots for e in err]
        return scaled_up_error

    def _cap_top_perc(self, df, top_perc):
        df_to_remove = df.iloc[int(len(df) * top_perc):]
        strings_to_remove = df_to_remove["string"].tolist()
        df = df[~df["string"].isin(strings_to_remove)]
        return df

    def plot_most_divergent_output(self, top_perc=.25, figsize=(10, 6)):
        plt.figure(figsize=figsize)
        df = self.df_joined
        df["diff"] = df["counter_x"] - df["counter_y"]
        df["diff"] = df["diff"].abs()
        df.sort_values(by="diff", ascending=False, inplace=True)
        df = self._cap_top_perc(df, top_perc)
        plt.figure(figsize=figsize)
        sns.barplot(x="string", y="diff", data=df)
        plt.xticks(rotation=90)
        plt.show()
