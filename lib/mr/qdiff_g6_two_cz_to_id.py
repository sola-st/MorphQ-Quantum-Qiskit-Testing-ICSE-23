import ast
from collections import Counter
import random
import numpy as np
import pandas as pd
from typing import List, Tuple, Dict, Any

from lib.mr import MetamorphicTransformation

import lib.metamorph as metamorph
from lib.qfl import detect_divergence


class QdiffG6TwoCzToId(MetamorphicTransformation):

    def check_precondition(self, code_of_source: str) -> bool:
        """Check if there are two CZ gates on the same bit."""
        sections = metamorph.get_sections(code_of_source)
        source_code_circuit = sections["CIRCUIT"]

        pairs = metamorph.get_consecutive_gates(
            source_code_circuit, gate_name="CZGate")
        self.pairs = pairs
        return len(self.pairs) > 0

    def is_semantically_equivalent(self) -> bool:
        return True

    def derive(self, code_of_source: str) -> str:
        """Replace two CZ gates on the same bit with an Identity gate."""
        add_identity_matrix = self.mr_config['add_identity_matrix']

        sections = metamorph.get_sections(code_of_source)
        source_code_circuit = sections["CIRCUIT"]

        pair_to_replace = random.choice(self.pairs)

        mr_metadata = {}
        mr_metadata["pair_to_replace"] = str(pair_to_replace)

        changed_section = source_code_circuit
        lines = source_code_circuit.split("\n")
        # remove the second occurrence of the CZ gate
        lines.pop(pair_to_replace["next_lineno"] - 1)

        # replace both positions with an id gate each, applied on the two bits
        lines.pop(pair_to_replace["lineno"] - 1)
        if add_identity_matrix:
            first_id_gate = \
                f'{pair_to_replace["circuit_id"]}.append(IGate(), ' + \
                f'qargs=[{pair_to_replace["qregs"][0]}[{pair_to_replace["qbits"][0]}]], cargs=[])'
            lines.insert(pair_to_replace["lineno"] - 1, first_id_gate)
            second_id_gate = \
                f'{pair_to_replace["circuit_id"]}.append(IGate(), ' + \
                f'qargs=[{pair_to_replace["qregs"][0]}[{pair_to_replace["qbits"][1]}]], cargs=[])'
            lines.insert(pair_to_replace["next_lineno"] - 1, second_id_gate)

        changed_section = "\n".join(lines)

        sections["CIRCUIT"] = changed_section

        self.metadata = mr_metadata

        return metamorph.reconstruct_sections(sections)
