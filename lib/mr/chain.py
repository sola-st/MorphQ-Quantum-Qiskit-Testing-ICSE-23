from typing import List, Tuple, Dict, Any
import random


from lib.mr import MetamorphicTransformation
from lib.mr import *


class ChainedTransformation(MetamorphicTransformation):

    def __init__(self, name: str,
                 metamorphic_strategies_config: Dict[str, Any],
                 detectors_config: Dict[str, Any],
                 seed: int = None):
        self.name = name
        if seed is not None:
            random.seed(seed)
        self.metamorphic_transformations = [
            eval(transf_name)(
                name=transf_name,
                metamorphic_strategies_config=metamorphic_strategies_config,
                detectors_config=detectors_config)
            for transf_name in metamorphic_strategies_config.keys()
        ]
        self.detectors = detectors_config
        self.metadata = {}
        self.transf_applied_count = 0

    def select_random_transformation(self):
        """Select a transformation from the list of transformations."""
        self.main_transformation = random.choice(
            self.metamorphic_transformations)

    def check_precondition(self, code_of_source: str):
        return self.main_transformation.check_precondition(code_of_source)

    def check_output_relationship(
            self,
            result_a: Dict[str, int],
            result_b: Dict[str, int]) -> bool:
        return self.main_transformation.check_output_relationship(
            result_a, result_b)

    def is_semantically_equivalent(self) -> bool:
        return self.main_transformation.is_semantically_equivalent()

    def derive(self, code_of_source: str) -> str:
        """Apply the main transformation and update the metadata and count."""
        print(f"Applying: {self.main_transformation}")
        new_source_code = \
            self.main_transformation.derive(code_of_source)
        self.metadata[self.transf_applied_count] = \
            self.main_transformation.metadata
        self.transf_applied_count += 1
        self.last_applied_transformation = self.main_transformation
        return new_source_code

    def get_name_current_transf(self):
        return self.main_transformation.__class__.__name__

    def get_last_applied_transformation(self):
        return self.last_applied_transformation
