import ast
from collections import Counter
import random
import numpy as np
import pandas as pd
from typing import List, Tuple, Dict, Any

from lib.mr import MetamorphicTransformation

import lib.metamorph as metamorph
from lib.qfl import detect_divergence


class QdiffG4ZtoSS(MetamorphicTransformation):

    def check_precondition(self, code_of_source: str) -> bool:
        """Check if there is any Z gate."""
        sections = metamorph.get_sections(code_of_source)
        source_code_circuit = sections["CIRCUIT"]
        instructions = metamorph.get_instructions(source_code_circuit)
        self.instruction_z_gate = [
            i for i in instructions if i["gate"] == "ZGate"]
        self.tot_n_z_gates = len(self.instruction_z_gate)
        return self.tot_n_z_gates > 0

    def is_semantically_equivalent(self) -> bool:
        return True

    def derive(self, code_of_source: str) -> str:
        """Replace a Z gate with two S gates."""
        min_to_change = self.mr_config['min_to_change']
        max_to_change = self.mr_config['max_to_change']
        n_gate_to_change = random.randint(min_to_change, max_to_change)
        max_to_change = min(n_gate_to_change, self.tot_n_z_gates)

        sections = metamorph.get_sections(code_of_source)
        source_code_circuit = sections["CIRCUIT"]

        z_gates_to_replace = random.sample(
            self.instruction_z_gate, max_to_change)

        mr_metadata = {}
        mr_metadata["z_gates_to_replace"] = str(z_gates_to_replace)

        changed_section = source_code_circuit
        lines = source_code_circuit.split("\n")

        z_gates_to_replace_reverse_order = sorted(
            z_gates_to_replace, key=lambda x: x["lineno"], reverse=True)
        # we start replacing gates, from the last one because each
        # substitution of a single makes the code longer.
        for z_gate in z_gates_to_replace_reverse_order:
            # remove gate
            edit_location = z_gate["lineno"] - 1
            lines.pop(edit_location)
            if z_gate["lineno"] != z_gate["end_lineno"]:
                # in case the gate spans in two lines, remove an extra line
                # we assume that it doesn't overflow to more than two lines.
                lines.pop(edit_location)
            bit_1 = z_gate["qbits"][0]
            circ_id = z_gate["circuit_id"]
            reg_id = z_gate["qregs"][0]
            # we assume that all the bits belong to the same register
            # insert the last as first
            last_s_gate = \
                f'{circ_id}.append(SGate(), ' + \
                f'qargs=[{reg_id}[{bit_1}]], cargs=[])'
            lines.insert(edit_location, last_s_gate)
            first_s_gate = \
                f'{circ_id}.append(SGate(), ' + \
                f'qargs=[{reg_id}[{bit_1}]], cargs=[])'
            lines.insert(edit_location, first_s_gate)

        changed_section = "\n".join(lines)

        sections["CIRCUIT"] = changed_section

        self.metadata = mr_metadata

        return metamorph.reconstruct_sections(sections)
