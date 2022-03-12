import ast
from functools import reduce
import numpy as np
import random
import re
from typing import List, Tuple, Dict, Any
import uuid

from lib.mr import MetamorphicTransformation

import lib.metamorph as metamorph
from lib.qfl import detect_divergence


class AddUnusedRegister(MetamorphicTransformation):

    def check_precondition(self, code_of_source: str) -> bool:
        sections = metamorph.get_sections(code_of_source)
        code_transpiler = sections["OPTIMIZATION_LEVEL"]
        is_coupling_map_free = \
            "coupling_map=None" in code_transpiler.replace(" ", "")
        return is_coupling_map_free

    def is_semantically_equivalent(self) -> bool:
        return True

    def derive(self, code_of_source: str) -> str:
        """Add unused Quantum registers.
        """
        min_n_bit = self.mr_config["min_n_bit"]
        max_n_bit = self.mr_config["max_n_bit"]
        reg_types = self.mr_config["reg_types"]

        n_bits = random.randint(min_n_bit, max_n_bit)

        sections = metamorph.get_sections(code_of_source)

        if "USELESS_ENTITIES" not in sections.keys():
            sections = metamorph.add_section(
                sections=sections,
                new_section_name="USELESS_ENTITIES",
                after_section="CIRCUIT")

        circuit = sections["CIRCUIT"]
        available_circuits = metamorph.get_circuits_used(
            circ_definition=circuit)
        circuit_to_extend = random.choice(available_circuits)

        register_type = random.choice(reg_types)
        reg_prefix = "qr" if register_type == "QuantumRegister" else "cr"
        new_id = f"{reg_prefix}_{uuid.uuid4().hex[:6]}"
        useless_code_area = "\n"
        useless_code_area += \
            f"{new_id} = {register_type}({n_bits}, name='{new_id}')\n"
        useless_code_area += \
            f"{circuit_to_extend['name']}.add_register({new_id})\n"
        sections["USELESS_ENTITIES"] = useless_code_area

        print(f"Follow: add {register_type}({n_bits})")

        mr_metadata = {
            "new_register_size": n_bits,
            "register_type": register_type
        }

        self.metadata = mr_metadata

        return metamorph.reconstruct_sections(sections)
