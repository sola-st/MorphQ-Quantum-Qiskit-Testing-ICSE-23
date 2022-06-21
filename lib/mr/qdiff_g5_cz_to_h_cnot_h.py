import ast
from collections import Counter
import random
import numpy as np
import pandas as pd
from typing import List, Tuple, Dict, Any

from lib.mr import MetamorphicTransformation

import lib.metamorph as metamorph
from lib.qfl import detect_divergence


class QdiffG5CZtoHCnotH(MetamorphicTransformation):

    def check_precondition(self, code_of_source: str) -> bool:
        """Check if there is any CZ gate."""
        sections = metamorph.get_sections(code_of_source)
        source_code_circuit = sections["CIRCUIT"]
        instructions = metamorph.get_instructions(source_code_circuit)
        self.instruction_cz_gate = [
            i for i in instructions if i["gate"] == "CZGate"]
        self.tot_n_cz_gates = len(self.instruction_cz_gate)
        return self.tot_n_cz_gates > 0

    def is_semantically_equivalent(self) -> bool:
        return True

    def derive(self, code_of_source: str) -> str:
        """Replace a CZ gate with H CNOT H."""
        min_to_change = self.mr_config['min_to_change']
        max_to_change = self.mr_config['max_to_change']
        n_gate_to_change = random.randint(min_to_change, max_to_change)
        max_to_change = min(n_gate_to_change, self.tot_n_cz_gates)

        sections = metamorph.get_sections(code_of_source)
        source_code_circuit = sections["CIRCUIT"]

        cz_gates_to_replace = random.sample(
            self.instruction_cz_gate, max_to_change)

        mr_metadata = {}
        mr_metadata["cz_gates_to_replace"] = str(cz_gates_to_replace)

        changed_section = source_code_circuit
        lines = source_code_circuit.split("\n")

        cz_gates_to_replace_reverse_order = sorted(
            cz_gates_to_replace, key=lambda x: x["lineno"], reverse=True)
        # we start replacing gates, from the last one because each
        # substitution of a single makes the code longer.
        for cz_gate in cz_gates_to_replace_reverse_order:
            # remove gate
            edit_location = cz_gate["lineno"] - 1
            lines.pop(edit_location)
            if cz_gate["lineno"] != cz_gate["end_lineno"]:
                # in case the gate spans in two lines, remove an extra line
                # we assume that it doesn't overflow to more than two lines.
                lines.pop(edit_location)
            bit_1 = cz_gate["qbits"][0]
            bit_2 = cz_gate["qbits"][1]
            circ_id = cz_gate["circuit_id"]
            reg_id = cz_gate["qregs"][0]
            # we assume that all the bits belong to the same register
            # insert the last as first
            last_h_gate = \
                f'{circ_id}.append(HGate(), ' + \
                f'qargs=[{reg_id}[{bit_2}]], cargs=[])'
            lines.insert(edit_location, last_h_gate)
            cnot_gate = \
                f'{circ_id}.append(CXGate(), ' + \
                f'qargs=[{reg_id}[{bit_1}], {reg_id}[{bit_2}]], cargs=[])'
            lines.insert(edit_location, cnot_gate)
            first_h_gate = \
                f'{circ_id}.append(HGate(), ' + \
                f'qargs=[{reg_id}[{bit_2}]], cargs=[])'
            lines.insert(edit_location, first_h_gate)

        changed_section = "\n".join(lines)

        sections["CIRCUIT"] = changed_section

        self.metadata = mr_metadata

        return metamorph.reconstruct_sections(sections)
