"""Metamorphic relationships and circuit manipulations for Qiskit.

"""

import numpy as np

import qiskit
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit import Aer, transpile
from qiskit.tools.visualization import circuit_drawer
from qiskit.quantum_info import state_fidelity

from typing import List, Dict, Any
import re
import ast
import astunparse

from importlib import import_module
from sys import version_info

from copy import deepcopy


def get_sections(circ_source_code: str) -> Dict[str, str]:
    """Extract the main sections in the generated code file.

    Note that the sections are separated by comments like this:
    # SECTION
    # NAME: PROLOGUE

    This method return the sections as a dictionary, where the key is the name
    of the section, and the value is the source code of the section.
    """
    section_contents = circ_source_code.split("# SECTION\n")
    regex_name_extr = r"^# NAME:\s([a-zA-Z_]+)\s"
    named_sections = {
        re.match(regex_name_extr, content).group(1): remove_comments(content)
        for content in section_contents
        if re.match(regex_name_extr, content) is not None
    }
    return named_sections

def reconstruct_sections(sections: Dict[str, str]) -> str:
    """Reconstruct the source code from the sections.

    Args:
        sections: The sections of the circuit.

    Returns:
        The source code of the circuit with the sections reconstructed.
    """
    reconstructed_source_code = ""
    for section_name, section_content in sections.items():
        reconstructed_source_code += f"# SECTION\n# NAME: {section_name}\n"
        reconstructed_source_code += section_content
    return reconstructed_source_code

def remove_comments(source_code: str) -> str:
    """Remove comments from the source code via ast.

    Note that the comments are separated by lines like this:
    # COMMENT
    """
    return astunparse.unparse(ast.parse(source_code))


def get_registers_used(circ_definition: str) -> List[Dict[str, Any]]:
    """Extract the available quantum and classical registers.

    For each register in the main program report:
    - the number of qubit used
    - the identifier name
    - the type or register
    """
    tree = ast.parse(circ_definition)

    class RegisterHunter(ast.NodeVisitor):

        def __init__(self, register_type: str):
            self.register_type = register_type
            self.registers = []

        def visit(self, node: ast.AST):
            self.check_if_register(node)
            for child in ast.iter_child_nodes(node):
                self.visit(child)

        def check_if_register(self, node: ast.AST):
            if (isinstance(node, ast.Assign) and
                    isinstance(node.value, ast.Call) and
                    node.value.func.id in [
                            "QuantumRegister", "ClassicalRegister"] and
                    isinstance(node.value.args[0], ast.Constant)):
                register_type = node.value.func.id
                identifier = node.targets[0].id
                self.registers.append({
                    "name": identifier,
                    "type": register_type,
                    "size": node.value.args[0].value
                })

        def get_registers(self):
            return self.registers

    register_hunter = RegisterHunter("quantum")
    register_hunter.generic_visit(tree)
    return register_hunter.get_registers()


def to_code(node):
    """
    Convert the AST input to Python source string
    :param node: AST node
    :type node: ```AST```
    :return: Python source
    :rtype: ```str```
    """
    return (
        getattr(import_module("astor"), "to_source")
        if version_info[:2] < (3, 9)
        else getattr(import_module("ast"), "unparse")
    )(node)


def mr_change_backend(source_code: str, available_backends: str) -> str:
    """Change the backend used in the source code.

    Args:
        source_code: The source code of the circuit.
        available_backends: available backends to use.

    Returns:
        The source code of the circuit with the backend changed.
    """
    sections = get_sections(source_code)
    execution_section = sections["EXECUTION"]

    tree = ast.parse(execution_section)

    class BackendChanger(ast.NodeTransformer):

        def __init__(self, available_backends: List[str]):
            self.available_backends = deepcopy(available_backends)

        def visit_Call(self, node):
            if (isinstance(node, ast.Call) and
                    isinstance(node.func, ast.Attribute) and
                    node.func.attr == "get_backend" and
                    isinstance(node.args[0], ast.Constant)):
                if node.args[0].value in self.available_backends:
                    self.available_backends.remove(node.args[0].value)
                print(f"Found: {node.args[0].value}")
                node.args[0].value = np.random.choice(self.available_backends)
            return node

    backend_changer = BackendChanger(available_backends)
    modified_tree = backend_changer.visit(tree)
    changed_section = to_code(modified_tree)
    sections["EXECUTION"] = changed_section

    return reconstruct_sections(sections)

def mr_change_basic_gates(source_code: str, basic_gates: List[str]) -> str:
    """Change the basic gates used in the source code (via transpile).
    """
    pass