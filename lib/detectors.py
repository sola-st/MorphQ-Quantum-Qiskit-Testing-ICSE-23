"""Detector to check if the two distributions are significantly different."""

from abc import ABC
from abc import abstractmethod

from scipy.stats import kstest

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

    def check(self, result_A, result_B):
        """Compare two distributions with KS Test"""
        self.load_results(result_A, result_B)
        self.statistics, self.p_value = kstest(self.samples_A, self.samples_B)
        return self.statistics, self.p_value