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


class ToQasmAndBack(MetamorphicTransformation):

    def check_precondition(self, code_of_source: str) -> bool:
        sections = metamorph.get_sections(code_of_source)
        execution_area = sections["EXECUTION"]

        no_conversion = "QASM_CONVERSION" not in sections.keys()
        single_circuit_execution = execution_area.count("execute(") == 1

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
            r"\s=\sexecute\(([a-zA0-9_]+)", execution_area).group(1)

        qasm_conversion_area = "\n"
        qasm_conversion_area = f"{main_circuit_id} = " + \
            f"QuantumCircuit.from_qasm_str({main_circuit_id}.qasm())\n"
        sections["QASM_CONVERSION"] = qasm_conversion_area

        print(f"Follow: add '{main_circuit_id}' conversion to and from QASM " +
              f"(before: {before_section})")

        mr_metadata = {
            "before_section": before_section
        }

        self.metadata = mr_metadata

        return metamorph.reconstruct_sections(sections)
