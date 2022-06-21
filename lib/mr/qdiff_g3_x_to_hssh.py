import ast
from collections import Counter
import random
import numpy as np
import pandas as pd
from typing import List, Tuple, Dict, Any

from lib.mr import MetamorphicTransformation

import lib.metamorph as metamorph
from lib.qfl import detect_divergence


class QdiffG3XToHSSH(MetamorphicTransformation):

    def check_precondition(self, code_of_source: str) -> bool:
        """Check if there is at least ax X gate."""
        sections = metamorph.get_sections(code_of_source)
        source_code_circuit = sections["CIRCUIT"]
        instructions = metamorph.get_instructions(source_code_circuit)
        self.instruction_x_gate = [
            i for i in instructions if i["gate"] == "XGate"]
        self.tot_n_x_gates = len(self.instruction_x_gate)
        return self.tot_n_x_gates > 0

    def is_semantically_equivalent(self) -> bool:
        return True

    def derive(self, code_of_source: str) -> str:
        """Replace an X gate with H S S H single qubit gates."""
        min_to_change = self.mr_config['min_to_change']
        max_to_change = self.mr_config['max_to_change']
        n_gate_to_change = random.randint(min_to_change, max_to_change)
        max_to_change = min(n_gate_to_change, self.tot_n_x_gates)

        sections = metamorph.get_sections(code_of_source)
        source_code_circuit = sections["CIRCUIT"]

        x_gates_to_replace = random.sample(
            self.instruction_x_gate, max_to_change)

        mr_metadata = {}
        mr_metadata["x_gates_to_replace"] = str(x_gates_to_replace)

        changed_section = source_code_circuit
        lines = source_code_circuit.split("\n")

        x_gates_to_replace_reverse_order = sorted(
            x_gates_to_replace, key=lambda x: x["lineno"], reverse=True)
        # we start replacing gates, from the last one because each
        # substitution of an X gate makes the code longer.
        for x_gate in x_gates_to_replace_reverse_order:
            # remove gate
            edit_location = x_gate["lineno"] - 1
            removed_original = lines.pop(edit_location)

            h_gate_last = removed_original.replace("XGate", "HGate")
            lines.insert(edit_location, h_gate_last)
            s_gate_last = removed_original.replace("XGate", "SGate")
            lines.insert(edit_location, s_gate_last)
            s_gate_first = removed_original.replace("XGate", "SGate")
            lines.insert(edit_location, s_gate_first)
            h_gate_first = removed_original.replace("XGate", "HGate")
            lines.insert(edit_location, h_gate_first)

        changed_section = "\n".join(lines)

        sections["CIRCUIT"] = changed_section

        self.metadata = mr_metadata

        return metamorph.reconstruct_sections(sections)
