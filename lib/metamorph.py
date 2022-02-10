"""Metamorphic relationships and circuit manipulations for Qiskit.

"""

import random
import numpy as np
import scipy

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


def create_random_mapping(qubit_indices: List[int]):
    """Create a mapping between two sets of the same qubit indices."""
    qubit_indices = list(set(qubit_indices))
    target_qubits = deepcopy(qubit_indices)
    np.random.shuffle(target_qubits)
    return {int(k): int(v) for k, v in zip(qubit_indices, target_qubits)}


def create_random_coupling_map(n_nodes: int,
                               edge_density: float) -> List[List[int]]:
    """Create a random coupling map."""
    adjacency_matrix = scipy.sparse.random(
        n_nodes, n_nodes, density=edge_density, format='coo')
    return [[int(r), int(c)]
            for (r, c) in zip(adjacency_matrix.row, adjacency_matrix.col)]


def create_random_connected_coupling_map(
        n_nodes: int, edge_density: float, force_symmetric: bool = True) -> List[List[int]]:
    """Create a random coupling map which is connected.

    Inspired by: https://stackoverflow.com/a/2041539/13585425
    """
    m = np.zeros((n_nodes, n_nodes), dtype=int)

    # we remove n_nodes because we forbid the diagonal (self loops)
    possible_edges = (n_nodes * n_nodes) - n_nodes

    nodes_in_network = [0, 1]
    m[0, 1] = 1
    c_density = 1 / possible_edges

    nodes_out_of_network = list(
        set(list(range(n_nodes))).difference(set(nodes_in_network)))

    while c_density < edge_density or len(nodes_out_of_network) > 0:
        outgoing_edge = np.random.choice([True, False])

        # master node
        master_node = np.random.choice(nodes_in_network)
        # print(master_node)
        if outgoing_edge:
            direction_to_look_for = m[:, master_node]
        else:
            direction_to_look_for = m[master_node, :]
        if len(nodes_out_of_network) > 0:
            # reason: we want to include all the nodes in the network first,
            # then we care about density target
            available_targets = nodes_out_of_network
        else:
            available_targets = list(np.argwhere(~np.array(
                direction_to_look_for, dtype=bool)).flatten())
        if master_node in available_targets:
            # reason: to forbid self loops to be chosen
            available_targets.remove(master_node)
        if len(available_targets) > 0:
            # print(f"available_targets: {available_targets}")
            target_node = int(np.random.choice(available_targets))
            # print(f"target_node: {target_node}")
            if force_symmetric:
                m[master_node][target_node] = 1
                m[target_node][master_node] = 1
            else:
                if outgoing_edge:
                    m[master_node][target_node] = 1
                else:
                    m[target_node][master_node] = 1
        nodes_in_network.append(target_node)
        nodes_out_of_network = list(
            set(list(range(n_nodes))).difference(set(nodes_in_network)))
        # print(m)
        c_edges = np.sum(m)
        c_density = float(c_edges) / possible_edges

    adjacency_matrix = scipy.sparse.coo_matrix(m)
    return [[int(r), int(c)] for (r, c) in zip(
        adjacency_matrix.row, adjacency_matrix.col)]


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
    mr_metadata = {}

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
                target_backend = np.random.choice(self.available_backends)
                print(f"Follow: replace backend {node.args[0].value} -> " +
                      f"{target_backend}")
                mr_metadata["initial_backend"] = str(node.args[0].value)
                mr_metadata["new_backend"] = str(target_backend)
                node.args[0].value = target_backend
            return node

    backend_changer = BackendChanger(available_backends)
    modified_tree = backend_changer.visit(tree)
    changed_section = to_code(modified_tree)
    sections["EXECUTION"] = changed_section

    return reconstruct_sections(sections), mr_metadata


def mr_change_basis(source_code: str,
                    universal_gate_sets: List[Dict[str, Any]]) -> str:
    """Change the basic gates used in the source code (via transpile).
    """
    target_gates = np.random.choice(universal_gate_sets)["gates"]
    sections = get_sections(source_code)
    opt_level_section = sections["OPTIMIZATION_LEVEL"]
    mr_metadata = {}

    tree = ast.parse(opt_level_section)

    class BasisChanger(ast.NodeTransformer):

        def __init__(self, target_gates: List[str]):
            self.target_gates = target_gates

        def visit_Call(self, node):
            if (isinstance(node, ast.Call) and
                    isinstance(node.func, ast.Name) and
                    node.func.id == "transpile"):
                args = [k.arg for k in node.keywords]
                if "basis_gates" in args:
                    idx = args.index("basis_gates")
                    node.keywords[idx].value = ast.List(elts=[
                        ast.Constant(g_name) for g_name in self.target_gates
                    ])
                    mr_metadata["new_basis_gates"] = self.target_gates
                    print("Follow: gateset replaced with: ", self.target_gates)
            return node

    changer = BasisChanger(target_gates)
    modified_tree = changer.visit(tree)
    changed_section = to_code(modified_tree)
    sections["OPTIMIZATION_LEVEL"] = changed_section

    return reconstruct_sections(sections), mr_metadata


def mr_change_opt_level(source_code: str, levels: List[int]) -> str:
    """Change the optimization level (via transpile).
    """

    sections = get_sections(source_code)
    opt_level_section = sections["OPTIMIZATION_LEVEL"]
    mr_metadata = {}

    tree = ast.parse(opt_level_section)

    class OptLevelChanger(ast.NodeTransformer):

        def __init__(self, levels: int):
            self.levels = deepcopy(levels)

        def visit_Call(self, node):
            if (isinstance(node, ast.Call) and
                    isinstance(node.func, ast.Name) and
                    node.func.id == "transpile"):
                args = [k.arg for k in node.keywords]
                if "optimization_level" in args:
                    initial_level = node.keywords[
                        args.index("optimization_level")].value.value
                    self.levels.remove(initial_level)
                    target_opt_level = int(np.random.choice(self.levels))
                    node.keywords[args.index("optimization_level")].value = \
                        ast.Constant(target_opt_level)
                    mr_metadata["initial_level"] = int(initial_level)
                    mr_metadata["new_level"] = int(target_opt_level)
                    print(f"Follow: optimization level changed:" +
                          f" {initial_level} -> {target_opt_level}")
            return node

    changer = OptLevelChanger(levels)
    modified_tree = changer.visit(tree)
    changed_section = to_code(modified_tree)
    sections["OPTIMIZATION_LEVEL"] = changed_section

    return reconstruct_sections(sections), mr_metadata


def mr_change_coupling_map(source_code: str,
                           min_perc_nodes: float,
                           max_perc_nodes: float,
                           min_connection_density: float,
                           max_connection_density: float,
                           force_connected: bool = True,
                           force_symmetric: bool = True) -> str:
    """Change the coupling map.


    Note that the coupling map could be smaller or larger than the number of
    qubits in the original circuit.

    min_perc_nodes: defines the percentage reduction of the coupling map size
    with respect to the number of qubits in the circuit.

    max_perc_nodes: defines the percentage expansion of the coupling map size
    with respect to the number of qubits in the circuit.

    """
    sections = get_sections(source_code)
    opt_level_section = sections["OPTIMIZATION_LEVEL"]
    mr_metadata = {}

    tree = ast.parse(opt_level_section)

    source_code_circuit = sections["CIRCUIT"]
    registers = get_registers_used(source_code_circuit)
    # we assume to have exactly one quantum and one classical register
    # and they have the same number of qubits
    quantum_reg = [r for r in registers
                   if r["type"] == "QuantumRegister"][0]
    classical_reg = [r for r in registers
                     if r["type"] == "ClassicalRegister"][0]
    assert(quantum_reg["size"] == classical_reg["size"])

    n_bits_declared = quantum_reg["size"]
    n_bits = random.randint(
        int(n_bits_declared * min_perc_nodes),
        int(n_bits_declared * max_perc_nodes)
    )
    edge_density = random.uniform(
        min_connection_density, max_connection_density)

    if n_bits > 1:
        if force_connected:
            rnd_coupling_map = create_random_connected_coupling_map(
                n_nodes=n_bits, edge_density=edge_density,
                force_symmetric=force_symmetric)
        else:
            rnd_coupling_map = create_random_coupling_map(
                n_nodes=n_bits, edge_density=edge_density)
    else:
        rnd_coupling_map = [[e] for e in range(n_bits)]

    mr_metadata["edge_density"] = edge_density
    mr_metadata["new_coupling_map"] = rnd_coupling_map

    class CouplingChanger(ast.NodeTransformer):

        def __init__(self, new_coupling: List[List[int]]):
            self.new_coupling = deepcopy(new_coupling)

        def visit_Call(self, node):
            if (isinstance(node, ast.Call) and
                    isinstance(node.func, ast.Name) and
                    node.func.id == "transpile"):
                args = [k.arg for k in node.keywords]
                if "coupling_map" in args:
                    initial_map = \
                        node.keywords[args.index("coupling_map")].value.value
                    ast_list = ast.parse(str(self.new_coupling)).body[0].value
                    node.keywords[args.index("coupling_map")].value = ast_list
                    print(f"Follow: coupling map changed:" +
                          f"{initial_map} -> {self.new_coupling}")
            return node

    changer = CouplingChanger(rnd_coupling_map)
    modified_tree = changer.visit(tree)
    changed_section = to_code(modified_tree)
    sections["OPTIMIZATION_LEVEL"] = changed_section

    return reconstruct_sections(sections), mr_metadata


def mr_change_qubit_order(source_code: str, scramble_percentage: float) -> str:
    """Change the qubit order.
    """
    sections = get_sections(source_code)
    source_code_circuit = sections["CIRCUIT"]
    tree = ast.parse(source_code_circuit)
    mr_metadata = {}

    registers = get_registers_used(source_code_circuit)
    # we assume to have exactly one quantum and one classical register
    # and they have the same number of qubits
    quantum_reg = [r for r in registers
                   if r["type"] == "QuantumRegister"][0]
    classical_reg = [r for r in registers
                     if r["type"] == "ClassicalRegister"][0]
    assert(quantum_reg["size"] == classical_reg["size"])

    n_idx = quantum_reg["size"]
    idx_to_scramble = np.random.choice(
        list(range(n_idx)),
        size=int(n_idx*scramble_percentage), replace=False)
    mapping = create_random_mapping(idx_to_scramble)
    mr_metadata["mapping"] = str(mapping)

    class QubitOrderChanger(ast.NodeTransformer):

        def __init__(self,
                     id_quantum_reg: str,
                     id_classical_reg: str, mapping: Dict[int, int]):
            self.id_quantum_reg = id_quantum_reg
            self.id_classical_reg = id_classical_reg
            self.mapping = mapping

        def visit_Subscript(self, node):
            if (isinstance(node, ast.Subscript) and
                    isinstance(node.value, ast.Name) and
                    (node.value.id == self.id_quantum_reg or
                     node.value.id == self.id_classical_reg) and
                    isinstance(node.slice, ast.Index) and
                    isinstance(node.slice.value, ast.Constant) and
                    node.slice.value.value in self.mapping.keys()):
                node.slice.value.value = self.mapping[node.slice.value.value]
            return node

    changer = QubitOrderChanger(
        id_quantum_reg=quantum_reg["name"],
        id_classical_reg=classical_reg["name"],
        mapping=mapping)
    modified_tree = changer.visit(tree)
    print("Follow: indices mapping: ", mapping)
    changed_section = to_code(modified_tree)
    sections["CIRCUIT"] = changed_section

    helper_function = '''
def read_str_with_mapping(bitstring, direct_mapping):
    """Given a bitstring convert it to the original mapping."""
    n_bits = len(bitstring)
    bitstring = bitstring[::-1]
    return "".join([bitstring[direct_mapping[i]] for i in range(n_bits)])[::-1]
    '''
    full_mapping = {**mapping, **{
        i: i for i in range(n_idx) if i not in mapping.keys()}}

    conversion = '''
counts = {
    read_str_with_mapping(bitstring, ''' + f"{full_mapping}" + '''): freq
    for bitstring, freq in counts.items()
}
RESULT = counts
    '''

    sections["EXECUTION"] = sections["EXECUTION"].replace(
        "RESULT = counts",
        helper_function + conversion)

    return reconstruct_sections(sections), mr_metadata
