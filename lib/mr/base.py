from abc import ABC
from abc import abstractmethod
import random
from typing import List, Tuple, Dict, Any

from lib.qfl import detect_divergence


class MetamorphicTransformation(ABC):

    def __init__(self, name: str,
                 metamorphic_strategies_config: Dict[str, Any],
                 detectors_config: Dict[str, Any],
                 seed: int = None):
        self.name = name
        if seed is not None:
            random.seed(seed)
        classname = self.__class__.__name__
        if classname in metamorphic_strategies_config.keys():
            self.mr_config = metamorphic_strategies_config[classname]
        else:
            print(f"No config for this MR: {classname}")
        self.detectors = detectors_config
        self.metadata = {}

    @abstractmethod
    def check_precondition(self, code_of_source: str):
        pass

    @abstractmethod
    def derive(self, code_of_source: str) -> str:
        pass

    def check_output_relationship(
            self,
            result_a: Dict[str, int],
            result_b: Dict[str, int]) -> bool:
        """Check that the two results are equivalent."""
        exec_metadata = {
            "res_A": result_a,
            "res_B": result_b
        }
        detectors = self.detectors
        return detect_divergence(exec_metadata, detectors)

    @abstractmethod
    def is_semantically_equivalent(self) -> bool:
        pass

    def __str__(self):
        return f"MetamorphicTransformation({self.name})"

