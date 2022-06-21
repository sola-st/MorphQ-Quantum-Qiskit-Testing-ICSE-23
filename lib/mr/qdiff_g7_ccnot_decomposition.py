import ast
from collections import Counter
import random
import numpy as np
import pandas as pd
from typing import List, Tuple, Dict, Any

from lib.mr import MetamorphicTransformation

import lib.metamorph as metamorph
from lib.qfl import detect_divergence


class QdiffG7CCNOTDecomposition(MetamorphicTransformation):

    def check_precondition(self, code_of_source: str) -> bool:
        """Check if there is any CCNOT gate."""
        sections = metamorph.get_sections(code_of_source)
        source_code_circuit = sections["CIRCUIT"]
        instructions = metamorph.get_instructions(source_code_circuit)
        self.instruction_ccx_gate = [
            i for i in instructions if i["gate"] == "CCXGate"]
        self.tot_n_ccx_gates = len(self.instruction_ccx_gate)
        return self.tot_n_ccx_gates > 0

    def is_semantically_equivalent(self) -> bool:
        return True

    def derive(self, code_of_source: str) -> str:
        """Replace a CCX gate (Toffoli) with its decomposition.

        Follow the question:
        https://quantumcomputing.stackexchange.com/a/3944/18188
        """
        min_to_change = self.mr_config['min_to_change']
        max_to_change = self.mr_config['max_to_change']
        n_gate_to_change = random.randint(min_to_change, max_to_change)
        max_to_change = min(n_gate_to_change, self.tot_n_ccx_gates)

        sections = metamorph.get_sections(code_of_source)
        source_code_circuit = sections["CIRCUIT"]

        ccx_gates_to_replace = random.sample(
            self.instruction_ccx_gate, max_to_change)

        mr_metadata = {}
        mr_metadata["ccx_gates_to_replace"] = str(ccx_gates_to_replace)

        changed_section = source_code_circuit
        lines = source_code_circuit.split("\n")

        ccx_gates_to_replace_reverse_order = sorted(
            ccx_gates_to_replace, key=lambda x: x["lineno"], reverse=True)
        # we start replacing gates, from the last one because each
        # substitution of an X gate makes the code longer.
        for ccx_gate in ccx_gates_to_replace_reverse_order:
            # remove gate
            edit_location = ccx_gate["lineno"] - 1
            lines.pop(edit_location)
            if ccx_gate["lineno"] != ccx_gate["end_lineno"]:
                # in case the ccx spans in two lines, remove an extra line
                # we assume that it doesn't overflow to more than two lines.
                lines.pop(edit_location)
            top_bit = ccx_gate["qbits"][0]
            middle_bit = ccx_gate["qbits"][1]
            bottom_bit = ccx_gate["qbits"][2]
            circ_id = ccx_gate["circuit_id"]
            reg_id = ccx_gate["qregs"][0]
            # we assume that all the bits belong to the same register
            # insert the last first
            last_cx_gate = \
                f'{circ_id}.append(CXGate(), ' + \
                f'qargs=[{reg_id}[{top_bit}], {reg_id}[{middle_bit}]], cargs=[])'
            lines.insert(edit_location, last_cx_gate)
            t_gate_top = \
                f'{circ_id}.append(TGate(), ' + \
                f'qargs=[{reg_id}[{top_bit}]], cargs=[])'
            lines.insert(edit_location, t_gate_top)
            t_gate_mid_inverse = \
                f'{circ_id}.append(TGate().inverse(), ' + \
                f'qargs=[{reg_id}[{middle_bit}]], cargs=[])'
            lines.insert(edit_location, t_gate_mid_inverse)
            second_last_cx_gate = \
                f'{circ_id}.append(CXGate(), ' + \
                f'qargs=[{reg_id}[{top_bit}], {reg_id}[{middle_bit}]], cargs=[])'
            lines.insert(edit_location, second_last_cx_gate)
            h_gate_bottom = \
                f'{circ_id}.append(HGate(), ' + \
                f'qargs=[{reg_id}[{bottom_bit}]], cargs=[])'
            lines.insert(edit_location, h_gate_bottom)
            t_gate_mid = \
                f'{circ_id}.append(TGate(), ' + \
                f'qargs=[{reg_id}[{middle_bit}]], cargs=[])'
            lines.insert(edit_location, t_gate_mid)
            t_gate_bottom = \
                f'{circ_id}.append(TGate(), ' + \
                f'qargs=[{reg_id}[{bottom_bit}]], cargs=[])'
            lines.insert(edit_location, t_gate_bottom)
            last_top_bottom_cx_gate = \
                f'{circ_id}.append(CXGate(), ' + \
                f'qargs=[{reg_id}[{top_bit}], {reg_id}[{bottom_bit}]], cargs=[])'
            lines.insert(edit_location, last_top_bottom_cx_gate)
            t_gate_bottom_inverse = \
                f'{circ_id}.append(TGate().inverse(), ' + \
                f'qargs=[{reg_id}[{bottom_bit}]], cargs=[])'
            lines.insert(edit_location, t_gate_bottom_inverse)
            second_mid_bottom_cx_gate = \
                f'{circ_id}.append(CXGate(), ' + \
                f'qargs=[{reg_id}[{middle_bit}], {reg_id}[{bottom_bit}]], cargs=[])'
            lines.insert(edit_location, second_mid_bottom_cx_gate)
            t_gate_bottom = \
                f'{circ_id}.append(TGate(), ' + \
                f'qargs=[{reg_id}[{bottom_bit}]], cargs=[])'
            lines.insert(edit_location, t_gate_bottom)
            first_top_bottom_cx_gate = \
                f'{circ_id}.append(CXGate(), ' + \
                f'qargs=[{reg_id}[{top_bit}], {reg_id}[{bottom_bit}]], cargs=[])'
            lines.insert(edit_location, first_top_bottom_cx_gate)
            t_gate_bottom_inverse = \
                f'{circ_id}.append(TGate().inverse(), ' + \
                f'qargs=[{reg_id}[{bottom_bit}]], cargs=[])'
            lines.insert(edit_location, t_gate_bottom_inverse)
            first_mid_bottom_cx_gate = \
                f'{circ_id}.append(CXGate(), ' + \
                f'qargs=[{reg_id}[{middle_bit}], {reg_id}[{bottom_bit}]], cargs=[])'
            lines.insert(edit_location, first_mid_bottom_cx_gate)
            first_h_gate_bottom = \
                f'{circ_id}.append(HGate(), ' + \
                f'qargs=[{reg_id}[{bottom_bit}]], cargs=[])'
            lines.insert(edit_location, first_h_gate_bottom)

        changed_section = "\n".join(lines)

        sections["CIRCUIT"] = changed_section

        self.metadata = mr_metadata

        return metamorph.reconstruct_sections(sections)
