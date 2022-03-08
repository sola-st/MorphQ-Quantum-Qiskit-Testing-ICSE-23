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


class InjectParameters(MetamorphicTransformation):

    def check_precondition(self, code_of_source: str) -> bool:
        """Check if there are concrete values for gates params to replace."""
        class ConcreteParametersCounter(ast.NodeVisitor):

            def __init__(self):
                self.total_parameters = 0
                self.concrete_values = []

            def recursive(func):
                """ decorator to make visitor work recursive """
                def wrapper(self, node):
                    func(self, node)
                    for child in ast.iter_child_nodes(node):
                        self.visit(child)
                return wrapper

            @recursive
            def visit_Call(self, node):
                if (isinstance(node, ast.Call) and
                        isinstance(node.func, ast.Name) and
                        ("Gate" in node.func.id)):
                    params = [e for e in node.args
                              if isinstance(e, ast.Constant)]
                    self.total_parameters += len(params)
                    self.concrete_values += [p.value for p in params]

        tree = ast.parse(code_of_source)
        counter = ConcreteParametersCounter()
        counter.generic_visit(tree)
        self.concrete_values = counter.concrete_values
        # print("All concrete values:", self.concrete_values)

        sections = metamorph.get_sections(code_of_source)
        execution_area = sections["EXECUTION"]
        single_circuit_execution = execution_area.count("execute(") == 1

        return len(self.concrete_values) > 0 and single_circuit_execution

    def is_semantically_equivalent(self) -> bool:
        return True

    def derive(self, code_of_source: str) -> str:
        """Add unused Quantum registers.
        """
        min_n_params = self.mr_config["min_n_params"]
        max_n_params = self.mr_config["max_n_params"]
        if max_n_params is None or len(self.concrete_values) > max_n_params:
            max_n_params = len(self.concrete_values)

        values_to_change = random.randint(min_n_params, max_n_params)

        sections = metamorph.get_sections(code_of_source)

        if "PARAMETERS" not in sections.keys():
            sections = metamorph.add_section(
                sections=sections,
                new_section_name="PARAMETERS",
                after_section="PROLOGUE")

        if "PARAMETER_BINDING" not in sections.keys():
            sections = metamorph.add_section(
                sections=sections,
                new_section_name="PARAMETER_BINDING",
                after_section="MEASUREMENT")

        replacement_dict = {
            f"p_{uuid.uuid4().hex[:6]}": cv
            for cv in list(np.random.choice(
                self.concrete_values, size=values_to_change, replace=False))
        }
        # print("Replacement dict:", replacement_dict)
        # print("Values to change:", values_to_change)

        params_area = sections["PARAMETERS"]
        for param_id, param_cv in replacement_dict.items():
            params_area += f"{param_id} = Parameter('{param_id}')\n"
        sections["PARAMETERS"] = params_area + "\n"

        # get the main circuit with measurement to learn when to inject
        # parameters
        measurement_area = sections["MEASUREMENT"]
        main_circuit_id = re.search(
            r"([a-zA0-9_]+)\.measure", measurement_area).group(1)

        binding_area = sections["PARAMETER_BINDING"]
        binding_area = metamorph.remove_comments(binding_area)
        # print("Binding area: ", binding_area)
        if "bind_parameters" not in binding_area:
            binding_area += main_circuit_id + " = " \
                + main_circuit_id + ".bind_parameters({\n"
        else:
            binding_area = binding_area.replace("})", ",")
        for param_id, param_cv in replacement_dict.items():
            binding_area += f"    {param_id}: {param_cv},\n"
        binding_area += "})\n"
        sections["PARAMETER_BINDING"] = binding_area + "\n"
        # print("Binding area (AFTER): ", binding_area)

        class ParametrizeConcreteValues(ast.NodeTransformer):

            def __init__(self, replacement_dict: Dict[str, float]):
                self.replacement_dict = replacement_dict
                self.reverse_dict = {v: k for k, v in replacement_dict.items()}

            def visit_Call(self, node):
                self.generic_visit(node)
                if (isinstance(node, ast.Call) and
                        isinstance(node.func, ast.Name) and
                        ("Gate" in node.func.id)):
                    new_args = []
                    for e in node.args:
                        if isinstance(e, ast.Constant) and \
                                e.value in self.reverse_dict.keys():
                            new_param = ast.Name(
                                id=self.reverse_dict[e.value],
                                ctx=ast.Load())
                            new_args.append(new_param)
                        else:
                            new_args.append(e)
                    node.args = new_args
                return node

        circuit = sections["CIRCUIT"]
        tree = ast.parse(circuit)
        changer = ParametrizeConcreteValues(
            replacement_dict=replacement_dict)
        modified_tree = changer.visit(tree)
        changed_section = metamorph.to_code(modified_tree)
        sections["CIRCUIT"] = changed_section

        print(f"Follow: from concrete values to parameters " +
              f"({values_to_change}/{len(self.concrete_values)}):" +
              f"{replacement_dict}")

        mr_metadata = {
            "replacement_dictionary": replacement_dict,
        }

        self.metadata = mr_metadata

        return metamorph.reconstruct_sections(sections)
