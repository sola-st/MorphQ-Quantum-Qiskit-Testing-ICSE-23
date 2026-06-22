import ast
from functools import reduce
import numpy as np
import random
import re
from typing import List, Tuple, Dict, Any
import uuid

from lib.mr import MetamorphicTransformation

import lib.metamorph as metamorph
from lib.utils_qfl import detect_divergence


class ToQasmAndBack(MetamorphicTransformation):

    def check_precondition(self, code_of_source: str) -> bool:
        sections = metamorph.get_sections(code_of_source)
        execution_area = sections["EXECUTION"]

        no_conversion = "QASM_CONVERSION" not in sections.keys()
        single_circuit_execution = execution_area.count("sampler.run(") == 1

        return no_conversion and single_circuit_execution

    def is_semantically_equivalent(self) -> bool:
        return True

    def derive(self, code_of_source: str) -> str:
        """Add QASM section to convert it and back before execution.
        """
        qasm_version = self.mr_config["qasm_version"]
        before_sections = self.mr_config["before_sections"]

        before_section = random.choice(before_sections)

        sections = metamorph.get_sections(code_of_source)

        sections = metamorph.add_section(
            sections=sections,
            new_section_name="QASM_CONVERSION",
            before_section=before_section)

        execution_area = sections["EXECUTION"]
        main_circuit_id = re.search(
            r"\s=\stranspile\(([a-zA0-9_]+)", execution_area).group(1)

        # Checking which QASM version we are using
        if int(qasm_version) == 2:
            qasm_conversion_area = "\n"
            qasm_conversion_area += "from qiskit.qasm2 import dumps\n"
            qasm_conversion_area += "from qiskit.qasm2 import loads\n"
            qasm_conversion_area += "from qiskit.qasm2 import LEGACY_CUSTOM_INSTRUCTIONS\n"
            qasm_conversion_area += f"{main_circuit_id} = loads(dumps({main_circuit_id}), custom_instructions=LEGACY_CUSTOM_INSTRUCTIONS)\n"
            # qasm_conversion_area = f"{main_circuit_id} = " + \
            #     f"QuantumCircuit.from_qasm_str({main_circuit_id}.qasm())\n"
        elif int(qasm_version) == 3:
            qasm_conversion_area += "from qiskit import qasm3\n"
            qasm_conversion_area += (
                f"{main_circuit_id} = qasm3.loads("
                f"qasm3.dumps({main_circuit_id}))\n"
            )
        else:
            raise ValueError(f"Unsupported qasm_version: {qasm_version}")
    
        sections["QASM_CONVERSION"] = qasm_conversion_area

        print(f"Follow: add '{main_circuit_id}' conversion to and from QASM " +
              f"(before: {before_section})")

        mr_metadata = {
            "before_section": before_section
        }

        self.metadata = mr_metadata

        return metamorph.reconstruct_sections(sections)
