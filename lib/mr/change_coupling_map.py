
import ast
from copy import deepcopy
import random
from typing import List, Tuple, Dict, Any

import lib.metamorph as metamorph
from lib.mr import MetamorphicTransformation


class ChangeCouplingMap(MetamorphicTransformation):

    def check_precondition(self, code_of_source: str) -> bool:
        sections = metamorph.get_sections(code_of_source)
        if "USELESS_ENTITIES" not in sections.keys():
            return True
        new_register_added = "add_register" in sections["USELESS_ENTITIES"]
        return not new_register_added

    def is_semantically_equivalent(self) -> bool:
        return True

    def derive(self, code_of_source: str) -> str:
        """Change the coupling map.


        Note that the coupling map could be smaller or larger than the number of
        qubits in the original circuit.

        min_perc_nodes: defines the percentage reduction of the coupling map size
        with respect to the number of qubits in the circuit.

        max_perc_nodes: defines the percentage expansion of the coupling map size
        with respect to the number of qubits in the circuit.
        """

        min_perc_nodes = self.mr_config.get('min_perc_nodes')
        max_perc_nodes = self.mr_config.get('max_perc_nodes')
        min_connection_density = self.mr_config.get('min_connection_density')
        max_connection_density = self.mr_config.get('max_connection_density')
        force_connected = self.mr_config.get('force_connected', True)
        force_symmetric = self.mr_config.get('force_connected', True)

        sections = metamorph.get_sections(code_of_source)
        opt_level_section = sections["OPTIMIZATION_LEVEL"]
        mr_metadata = {}

        tree = ast.parse(opt_level_section)

        source_code_circuit = sections["CIRCUIT"]
        registers = metamorph.get_registers_used(source_code_circuit)
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
                rnd_coupling_map = metamorph.create_random_connected_coupling_map(
                    n_nodes=n_bits, edge_density=edge_density,
                    force_symmetric=force_symmetric)
            else:
                rnd_coupling_map = metamorph.create_random_coupling_map(
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
                        try:
                            initial_map = \
                                node.keywords[
                                    args.index("coupling_map")].value.value
                        except AttributeError:
                            # with a list the value attribute is not present
                            # this happends when the coupling map is a list
                            initial_map = metamorph.to_code(
                                node.keywords[args.index("coupling_map")].value)
                        ast_list = ast.parse(str(self.new_coupling)).body[0].value
                        node.keywords[args.index("coupling_map")].value = ast_list
                        print(f"Follow: coupling map changed: " +
                            f"{initial_map} -> {self.new_coupling}")
                return node

        changer = CouplingChanger(rnd_coupling_map)
        modified_tree = changer.visit(tree)
        changed_section = metamorph.to_code(modified_tree)
        sections["OPTIMIZATION_LEVEL"] = changed_section

        self.metadata = mr_metadata

        return metamorph.reconstruct_sections(sections)
