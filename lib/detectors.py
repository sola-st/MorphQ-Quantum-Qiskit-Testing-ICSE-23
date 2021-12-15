"""Detector to check if the two distributions are significantly different."""

from abc import ABC
from abc import abstractmethod

from scipy.stats import ks_2samp
import numpy as np

import torch
from torch_two_sample import statistics_diff

def obtain_raw_samples(summary_dict, representation='binary'):
    """Create raw samples.
    Params:
    - representation (default: 'binary')
        'binary', you get the string representation.
        'natural', you get the natural int representation.
    """
    raw_samples = []
    for value in summary_dict.keys():
        occurrences_of_value = summary_dict[value]
        if representation == 'natural':
            value = int(value, 2)
        raw_samples.extend([value] * occurrences_of_value)

    return raw_samples


class Detector(ABC):

    def load_results(self, result_A, result_B):
        self.statistics = None
        self.p_value = None
        self.result_A = result_A
        self.result_B = result_B
        self.samples_A = obtain_raw_samples(result_A)
        self.samples_B = obtain_raw_samples(result_B)

    @abstractmethod
    def check(self, result_A, result_B):
        """Check if the two distributions are significantly different."""
        pass


class KS_Detector(Detector):

    def __init__(self):
        self.name = "Kolmogorov–Smirnov Test"

    def check(self, result_A, result_B, random_seed=None):
        """Compare two distributions with KS Test"""
        self.load_results(result_A, result_B)
        self.statistics, self.p_value = ks_2samp(self.samples_A, self.samples_B)
        return self.statistics, self.p_value


class Energy_Detector(Detector):

    def __init__(self):
        self.name = "Energy Statistic"

    def check(self, result_A, result_B, random_seed=None):
        """Compare two distributions with Energy Test"""
        self.load_results(result_A, result_B)
        # convert the binary string in a vector
        n_subsamples = 100

        if random_seed is not None:
            np.random.seed(random_seed)
        print(f"WARINGING: subsampling {str(n_subsamples)} samples")
        self.samples_A = np.random.choice(self.samples_A, size=n_subsamples, replace=False)
        self.samples_B = np.random.choice(self.samples_B, size=n_subsamples, replace=False)

        n1 = len(self.samples_A)
        n2 = len(self.samples_B)
        binary_sample_A = np.vstack([
            np.array([int(x) for x in bin_string])
            for bin_string in self.samples_A
        ])
        binary_sample_B = np.vstack([
            np.array([int(x) for x in bin_string])
            for bin_string in self.samples_B
        ])
        sample_1 = torch.from_numpy(binary_sample_A)
        sample_2 = torch.from_numpy(binary_sample_B)
        energy_test = statistics_diff.EnergyStatistic(n1, n2)
        self.statistics, dist_matrix = energy_test.__call__(sample_1, sample_2, ret_matrix=True)
        dist_matrix = dist_matrix.to(torch.float32)
        self.p_value = energy_test.pval(dist_matrix, n_permutations=1000)
        if isinstance(self.p_value, torch.Tensor):
            self.p_value = self.p_value.item()
        if isinstance(self.statistics, torch.Tensor):
            self.statistics = self.statistics.item()
        return self.statistics, self.p_value
