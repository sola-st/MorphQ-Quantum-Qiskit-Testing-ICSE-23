import pandas as pd

from timeit import default_timer as timer

from lib.utils_db import get_database_connection
from lib.utils_db import update_database
from lib.utils_db import get_program_ids_in_table

from lib.detectors import *

from typing import List, Dict, Any
from math import sqrt
from lib.utils import create_folder_structure


# QFL utils


def estimate_n_samples_needed(
        config: Dict[str, Any],
        n_measured_qubits: int = 1,
        platform: str = None,
        backend: str = None):
    """Estimate the number of samples needed for a reliable comparison."""
    # based on the key strategy_sample_size_estimation
    if config["strategy_sample_size_estimation"] is None:
        return config["fixed_sample_size"]
    elif config["strategy_sample_size_estimation"] == "qdiff":
        user_defined_threshold = config["qdiff_user_defined_threshold"]
        confidence_level = config["qdiff_confidence_level"]
        n_quantum_states = 2**n_measured_qubits
        return int(
            (1 / sqrt(1 - confidence_level)) * sqrt(n_quantum_states) *
            (user_defined_threshold) ** (-2))


def setup_environment(
        experiment_folder: str = None,
        folder_structure: str = None):
    """Setup the environment."""
    create_folder_structure(
        parent_folder=experiment_folder,
        structure=folder_structure)


def scan_for_divergence(config: Dict[str, Any], test_name: str = 'ks',
                        alpha_level: int = 0.05, method="holm"):
    """Scan for divergence in the table."""
    con = get_database_connection(config, "qfl.db")
    df = pd.read_sql("SELECT * FROM QFLDATA", con)
    pval_col = f"divergence.{test_name}.p-value"
    df_sorted_pvals = df.sort_values(by=[pval_col])
    k = len(df_sorted_pvals)
    i_star = None
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
        if P_i > threshold:
            i_star = i
            print(f"i*: {i_star}")
            break
    if i_star is None:
        df_divergent = df_sorted_pvals
    else:
        df_divergent = df_sorted_pvals.iloc[:i_star]
    all_program_ids = get_program_ids_in_table(con, table_name='DIVERGENCE')
    new_df_divergent = df_divergent[
        ~df_divergent["program_id"].isin(all_program_ids)]
    if len(new_df_divergent) > 0:
        print(f"{len(new_df_divergent)} new divergent programs found.")
        print(new_df_divergent)
        for record in new_df_divergent.to_dict(orient='records'):
            update_database(con, "DIVERGENCE", record)
    con.close()


def detect_divergence(exec_metadata, detectors: List[Dict[str, Any]] = None):
    """Detect divergence with all the detectors and save the results."""
    results = {}
    for detector_config in detectors:
        detector_name = detector_config["name"]
        start_check = timer()
        detector = eval(detector_config["detector_object"])()
        stat, pval = detector.check(
            result_A=exec_metadata['res_A'],
            result_B=exec_metadata['res_B'])
        end_check = timer()
        time_check = end_check - start_check
        results[detector_name] = {"statistic": stat,
                                  "p-value": pval, "time": time_check}
    return results
