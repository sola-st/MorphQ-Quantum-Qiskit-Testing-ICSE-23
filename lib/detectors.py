"""Detector to check if the two distributions are significantly different."""

from abc import ABC
from abc import abstractmethod

from scipy.stats import ks_2samp
import numpy as np

import torch
from scipy.spatial.distance import jensenshannon
from lib.inspector import convert_dict_to_df


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


def obtain_multivariate_samples(summary_dict):
    """Create raw samples with multivariate representation.

    Note that each outcome is now a sequence of random variable [0,1]
    and not a bit string.
    """
    samples = obtain_raw_samples(summary_dict, representation='binary')
    multivariate_samples = np.vstack([
        np.array([int(x) for x in bin_string])
        for bin_string in samples
    ])
    return multivariate_samples


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
        return self.statistics, np.float64(self.p_value)


class JS_Detector(Detector):

    def __init__(self):
        self.name = "Jensen–Shannon Distance"

    def check(self, result_A, result_B, random_seed=None):
        """Compare two distributions with JS Distance"""
        df = convert_dict_to_df(
            result_A, result_B, platform_a='A', platform_b='B')
        df = df.pivot(index='name', columns='string', values='counter')
        df = df.fillna(0)
        self.statistics = jensenshannon(p=list(df.loc["A"]), q=list(df.loc["B"]))
        self.p_value = -1
        return self.statistics, np.float64(self.p_value)




class ChiSquare_Detector(Detector):

    def __init__(self):
        self.name = "Chi-Square Test"

    def check(self, result_A, result_B, random_seed=None):
        """Compare two distributions with Chi-Square Test"""
        return 0, 0
        #self.load_results(result_A, result_B)
        #self.statistics, self.p_value = ks_2samp(self.samples_A, self.samples_B)
        #return self.statistics, self.p_value


class Faster_Energy_Detector(Detector):

    def __init__(self) -> None:
        self.name = "Energy Statistic (faster distance)"

    def check(self, result_A, result_B, random_seed=None):
        """Compare two distributions with Energy Statistic"""
        self.statistics = self.energy_call(result_A, result_B)
        self.p_value = -1
        cut_off = 0.001
        if self.statistics < cut_off:
            self.p_value = 1
        else:
            self.p_value = 10e-6
        if isinstance(self.p_value, torch.Tensor):
            self.p_value = self.p_value.item()
        if isinstance(self.statistics, torch.Tensor):
            self.statistics = self.statistics.item()
        return self.statistics, self.p_value

    def unique_multivariates_and_frequencies(self, result_dictionary):
        """Return keys as multivariate vectors and their frequecies."""
        keys, frequencies = zip(*result_dictionary.items())
        multivariate_keys = np.vstack([
            np.array([int(x) for x in bin_string])
            for bin_string in keys
        ])
        return multivariate_keys, frequencies

    def pdist(self, sample_1, sample_2, norm=2, eps=1e-5):
        r"""Compute the matrix of all squared pairwise distances.
        Arguments
        ---------
        sample_1 : torch.Tensor or Variable
            The first sample, should be of shape ``(n_1, d)``.
        sample_2 : torch.Tensor or Variable
            The second sample, should be of shape ``(n_2, d)``.
        norm : float
            The l_p norm to be used.
        Returns
        -------
        torch.Tensor or Variable
            Matrix of shape (n_1, n_2). The [i, j]-th entry is equal to
            ``|| sample_1[i, :] - sample_2[j, :] ||_p``."""
        n_1, n_2 = sample_1.size(0), sample_2.size(0)
        norm = float(norm)
        if norm == 2.:
            norms_1 = torch.sum(sample_1**2, dim=1, keepdim=True)
            norms_2 = torch.sum(sample_2**2, dim=1, keepdim=True)
            norms = (norms_1.expand(n_1, n_2) +
                    norms_2.transpose(0, 1).expand(n_1, n_2))
            distances_squared = norms - 2 * sample_1.mm(sample_2.t())
            return torch.sqrt(eps + torch.abs(distances_squared))
        else:
            dim = sample_1.size(1)
            expanded_1 = sample_1.unsqueeze(1).expand(n_1, n_2, dim)
            expanded_2 = sample_2.unsqueeze(0).expand(n_1, n_2, dim)
            differences = torch.abs(expanded_1 - expanded_2) ** norm
            inner = torch.sum(differences, dim=2, keepdim=False)
            return (eps + inner) ** (1. / norm)

    def increase_dimension(self, small_matrix, record_frequencies):
        """Duplicate row and column based on the frquencies.

        Note that record_frequencies contains record like:

        7: 128,

        which means that the row and column 7 have to be replicated 128 times,
        vertically and horizontally respectively.
        """
        repeat_tensor = torch.tensor(np.array(record_frequencies))
        # print(repeat_tensor)
        small_matrix = torch.repeat_interleave(small_matrix, repeat_tensor, dim=1)
        small_matrix = torch.repeat_interleave(small_matrix, repeat_tensor, dim=0)
        # print(small_matrix)
        return small_matrix

    def energy_call(self, res_1, res_2):

            values_1, freq_1 = self.unique_multivariates_and_frequencies(result_dictionary=res_1)
            values_2, freq_2 = self.unique_multivariates_and_frequencies(result_dictionary=res_2)


            values_1 = torch.from_numpy(values_1)
            values_2 = torch.from_numpy(values_2)
            sample_12 = torch.cat((values_1, values_2), 0)

            small_matrix = self.pdist(sample_12, sample_12, norm=2)
            distances = self.increase_dimension(
                small_matrix=small_matrix,
                record_frequencies=np.hstack((np.array(freq_1), np.array(freq_2))))
            #distances = pdist(sample_12, sample_12, norm=2)

            n_1 = sum(freq_1)
            print("n_1:", n_1)
            n_2 = sum(freq_2)
            a00 = - 1. / (n_1 * n_1)
            a11 = - 1. / (n_2 * n_2)
            a01 = 1. / (n_1 * n_2)
            print("a00:", a00)
            print("a11:", a11)
            print("a01:", a01)

            d_1 = distances[:n_1, :n_1].sum()
            d_2 = distances[-n_2:, -n_2:].sum()
            d_12 = distances[:n_1, -n_2:].sum()
            print("d_1:", d_1)
            print("d_2:", d_2)
            print("d_12:", d_12)

            loss = 2 * a01 * d_12 + a00 * d_1 + a11 * d_2
            print("loss:", loss)
            print(type(loss))
            return loss


class Energy_Detector(Detector):

    def __init__(self):
        self.name = "Energy Statistic"

    def check(self, result_A, result_B, random_seed=None):
        """Compare two distributions with Energy Test"""
        try:
            from torch_two_sample import statistics_diff
        except ImportError:
            raise ImportError(
                "torch_two_sample is not installed. " +
                "Please install it from " +
                "https://github.com/josipd/torch-two-sample.")
        self.load_results(result_A, result_B)
        # convert the binary string in a vector
        n_subsamples = 100

        if random_seed is not None:
            np.random.seed(random_seed)

        #print(f"WARINGING: subsampling {str(n_subsamples)} samples")
        #self.samples_A = np.random.choice(self.samples_A, size=n_subsamples, replace=False)
        #self.samples_B = np.random.choice(self.samples_B, size=n_subsamples, replace=False)

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
        # self.p_value = energy_test.pval(dist_matrix, n_permutations=1000)
        self.p_value = -1
        cut_off = 0.001
        if self.statistics < cut_off:
            self.p_value = 1
        else:
            self.p_value = 10e-6
        if isinstance(self.p_value, torch.Tensor):
            self.p_value = self.p_value.item()
        if isinstance(self.statistics, torch.Tensor):
            self.statistics = self.statistics.item()
        return self.statistics, self.p_value
