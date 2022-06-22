"""
This file inspects a specific divergent comparison to find the root cause.

It includes also methods to store copies of interesting files in a
separate folder.
"""


# import libraries
from copy import deepcopy
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import os
from os.path import join
import pandas as pd
import pathlib
from termcolor import colored
import seaborn as sns
import shutil
from typing import List, Tuple, Dict, Any


from lib.utils import load_json, load_multiple_json


def convert_dict_to_df(res_a, res_b, platform_a, platform_b):
    """Convert two dictionary of execturions in a dataframe.

    Note that each record fives info about:
    - platform (column name: "name")
    - output string (column name: "string")
    - frequency (column name: "counter")
    """
    p1_strings, p1_counters = list(zip(*list(res_a.items())))
    p1_names = [f"{platform_a}"
                for _ in range(len(p1_strings))]
    p2_strings, p2_counters = list(zip(*list(res_b.items())))
    p2_names = [f"{platform_b}"
                for _ in range(len(p2_strings))]
    all_strings = p1_strings + p2_strings
    all_counters = p1_counters + p2_counters
    all_names = p1_names + p2_names
    df = pd.DataFrame(zip(all_strings, all_counters, all_names), columns=["string", "counter", "name"])
    df = df.sort_values(by=["counter"], ascending=False)
    return df


def retrieve_relevant_file_paths(
        experiment_folder: str,
        program_id: str,
        root_folder: str = "../data"):
    """Create the file paths."""
    main_path = os.path.join(root_folder, experiment_folder, "programs")
    path_dict = {
        "source": join(main_path, "source", f"{program_id}.py"),
        "followup": join(main_path, "followup", f"{program_id}.py"),
        "metadata": join(main_path, "metadata", f"{program_id}.json"),
        "metadata_exec": join(main_path, "metadata_exec", f"{program_id}.json")
    }
    return path_dict


def read_program(path: str, color='black'):
    file_content = open(path, 'r').read()
    print(colored(file_content, color))
    return file_content



def create_folder_in_interesting_cases(
        experiment_folder: str,
        program_id: str,
        root_folder: str = "../intersting_cases/metamorphic_testing"):
    """Create destination folder for the relevant files."""
    number = "".join([c for c in experiment_folder if c.isdigit()])
    new_folder_name = f"{number}_{program_id[:6]}"
    new_folder_path = os.path.join(root_folder, new_folder_name)
    pathlib.Path(new_folder_path).mkdir(parents=True, exist_ok=True)
    return new_folder_path


def copy_bug(
        experiment_folder: str,
        program_id: str,
        root_data_folder: str = "../data",
        root_bug_folder: str = "../intersting_cases/metamorphic_testing"):
    """Copy all the files of the interesting bug."""
    dest_folder = create_folder_in_interesting_cases(
        experiment_folder=experiment_folder,
        program_id=program_id,
        root_folder=root_bug_folder
    )

    original_file_paths = retrieve_relevant_file_paths(
        experiment_folder=experiment_folder,
        program_id=program_id,
        root_folder=root_data_folder
    )

    for k, original_file_path in original_file_paths.items():
        basename = os.path.basename(original_file_path)
        dest_file_path = join(dest_folder, f"{k}_{basename}")
        print(f"Copying... from {original_file_path} to {dest_file_path}")
        try:
            shutil.copy(original_file_path, dest_file_path)
        except FileNotFoundError as e:
            print(e)


def normalize_names(df: pd.DataFrame,
                    col: str, mapping: List[Tuple[str, str]]):
    """Replace the value of the given column according to the mapping.

    Each cell that contains the first string, will be replaced completely
    with the second string of the tuple."""
    df = deepcopy(df)
    for hook, replacement in mapping:
        df.loc[df[col].str.contains(hook), col] = replacement
    return df


def cluster_warnings(
        df: pd.DataFrame, warning_col: str, cluster_config: Dict[str, Any]):
    """Cluster the warnings based the given cluster configuration.

    Return: pd.DataFrame
        initial dataframe with new columns:
        - cluster_id
        - category: BUG, FP, UNCLEAR
        - short_desc: short description
        - etc. the other columns can be see in the configuration file
        in the cluster section
    """
    df = deepcopy(df)
    df_clusters = pd.json_normalize(cluster_config["clusters"])
    # create a default no cluster category
    df["cluster_id"] = "C_0"
    for cluster_rule in cluster_config["clustering_rules"]:
        hook = cluster_rule["hook"]
        replacement = cluster_rule["cluster_id"]
        if cluster_rule["type"] == "substring":
            df.loc[df[warning_col].str.contains(hook), "cluster_id"] = \
                replacement
        elif cluster_rule["type"] == "regex":
            df.loc[df[warning_col].str.contains(hook, regex=True), "cluster_id"] = replacement
    df_augmented = pd.merge(
        left=df,
        right=df_clusters,
        on="cluster_id"
    )
    return df_augmented


def inspec_column_of(df, program_id: str, target_col: str):
    """Inspect the value of a specific column given the program id."""
    df_single = df[df["program_id"] == program_id]
    print(f"n hits: {len(df_single)}")
    df_single = df_single.iloc[0]
    print(df_single[target_col])


def scan_log_for(log_lines: List[str],
                 target_string: str,
                 exclude_string: str = None,
                 neighborhood: int = 3):
    """Returns all the lines with the target string."""
    relevant_lines: List[List[str]] = []
    i: int = 0
    for line in log_lines:
        if target_string in line:
            if exclude_string is not None and exclude_string in line:
                continue
            relevant_lines.append(log_lines[i-neighborhood : i+neighborhood])
        i = i + 1
    return relevant_lines


def get_alarms_with_method(df, pval_col: str, alpha_level: float, method: str):
    """Get the program ids of the warnings raised by a method."""
    df_sorted_pvals = df.sort_values(by=[pval_col])
    k = len(df_sorted_pvals)
    i_star = None
    program_ids = []
    for i, (idx, row) in enumerate(df_sorted_pvals.iterrows()):
        ordinal_i = i + 1
        P_i = row[pval_col]
        if method == 'holm':
            threshold = alpha_level / (k - ordinal_i + 1)
        elif method == 'bonferroni':
            threshold = alpha_level / (k)
        elif method == 'bh':
            threshold = (alpha_level / (k)) * ordinal_i
        # print(f"(i: {ordinal_i}) current p-value: {P_i} vs threshold: {threshold}")
        elif method == 'static':
            threshold = alpha_level
        if P_i > threshold:
            i_star = i
            #print(f"i*: {i_star}")
            break
        program_ids.append(row["program_id"])
    return program_ids


def count_alarms_with_method(df, pval_col: str, alpha_level: float, method: str):
    """Count the number of warnings raised by a method."""
    return len(get_alarms_with_method(
        df=df,
        pval_col=pval_col,
        alpha_level=alpha_level,
        method=method
    ))


def get_first_n(df, col_time: str, n=1000):
    """Get the first n records as ordered by the time column."""
    return df.sort_values(by=col_time).iloc[:n]


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
        df = convert_dict_to_df(
            res_a=self.p1_results,
            res_b=self.p2_results,
            platform_a=self.platform_names[0],
            platform_b=self.platform_names[1]
        )
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

    def plot_histogram_together(self, top_perc=.25, max_solutions=50, figsize=(10, 6)):
        """Plot the histogram together for both platforms.

        The histogram will contain the top_perc of the solutions or at max
        a certain number of solutions (max_solution). Whatever is smaller.

        Note that the top_perc is the percentage of the top solutions to plot.
        """
        df = self.df_melted
        # to compute with the full dataset
        n_shots = df["counter"].sum() / 2  # because we have two platforms
        max_value = df["counter"].max()
        n_qubits = len(str(df.iloc[0]["string"]))

        df = self._cap_top_perc(df, top_perc)
        if len(df) > max_solutions:
            df = df.iloc[:max_solutions]

        print(f"n_qubits: {n_qubits}")
        print(f"n_shots: {n_shots}")
        uniform_threshold = ((1 / (2 ** n_qubits)) * n_shots)
        print(f"Uniform threshold: {uniform_threshold}")
        plt.figure(figsize=figsize)
        sns.barplot(x="string", hue="name", y="counter", data=df)
        if uniform_threshold < max_value * 1.1:
            plt.axhline(y=uniform_threshold, color="red", linestyle="--")
        else:
            plt.gca().set_facecolor("violet")
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
        df_grouped = df.groupby(["string"])["counter"].max().reset_index()
        df_grouped = df_grouped.sort_values(by="counter", ascending=False)
        all_strings_appeared = df_grouped["string"].tolist()
        strings_to_remove = all_strings_appeared[int(len(df) * top_perc):]
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


class OneNightStandInspector(object):

    def __init__(self, count_res_a, count_res_b, name_a='exec_a', name_b='exec_b', top_perc=.25, max_solutions=50, figsize=(10, 6)):
        """Plot the histogram together for both platforms.

        The histogram will contain the top_perc of the solutions or at max
        a certain number of solutions (max_solution). Whatever is smaller.

        Note that the top_perc is the percentage of the top solutions to plot.
        """
        df = convert_dict_to_df(
            res_a=count_res_a,
            res_b=count_res_b,
            platform_a=name_a,
            platform_b=name_b
        )
        # to compute with the full dataset
        n_shots_platform_a = df.where(df["name"] == name_a)["counter"].sum()
        n_shots_platform_b = df.where(df["name"] == name_b)["counter"].sum()
        df_normalized = df.copy()
        df_normalized["counter"] = df_normalized.apply(
            lambda row:
                row["counter"] / n_shots_platform_a
                if row["name"] == name_a
                else row["counter"] / n_shots_platform_b,
            axis=1)
        df = df_normalized
        max_value = df["counter"].max()
        n_qubits = len(str(df.iloc[0]["string"]))

        df = self._cap_top_perc(df, top_perc)
        if len(df) > max_solutions:
            df = df.iloc[:max_solutions]

        print(f"n_qubits: {n_qubits}")
        print(f"n_shots_platform_a: {n_shots_platform_a}")
        print(f"n_shots_platform_b: {n_shots_platform_b}")
        uniform_threshold = ((1 / (2 ** n_qubits)))
        print(f"Uniform threshold: {uniform_threshold}")
        plt.figure(figsize=figsize)
        sns.barplot(x="string", hue="name", y="counter", data=df)
        if uniform_threshold < max_value * 1.1:
            plt.axhline(y=uniform_threshold, color="red", linestyle="--")
        else:
            plt.gca().set_facecolor("violet")
        # rotate labels 90
        plt.xticks(rotation=90)
        plt.show()

    def _cap_top_perc(self, df, top_perc):
        df_grouped = df.groupby(["string"])["counter"].max().reset_index()
        df_grouped = df_grouped.sort_values(by="counter", ascending=False)
        all_strings_appeared = df_grouped["string"].tolist()
        strings_to_remove = all_strings_appeared[int(len(df) * top_perc):]
        df = df[~df["string"].isin(strings_to_remove)]
        return df