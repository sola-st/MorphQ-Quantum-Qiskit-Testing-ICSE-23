
import pytest
import ast
import astpretty
from qmt import get_mr_function_and_kwargs
from metamorph import *

config = {
    "metamorphic_strategies": [
        {'name': 'change_backend',
         'function': 'mr_change_backend',
         'kwargs': {'available_backends': ['aer_simulator',
                                           'aer_simulator_statevector',
                                           'aer_simulator_statevector_gpu',
                                           'aer_simulator_density_matrix_gpu',
                                           'aer_simulator_stabilizer',
                                           'aer_simulator_matrix_product_state']}},
        {'name': 'change_basis',
            'function': 'mr_change_basis',
            'kwargs': {'universal_gate_sets': [{'gates': ['rx', 'ry', 'rz', 'p', 'cx']},
                                               {'gates': [
                                                   'cx', 'h', 's', 't']},
                                               {'gates': ['ccx', 'h']}]}},
        {'name': 'change_opt_level',
            'function': 'mr_change_opt_level',
            'kwargs': {'levels': [0, 1, 2, 3]}},
        {'name': 'change_qubit_order',
            'function': 'mr_change_qubit_order',
            'kwargs': {'scramble_percentage': 0.5}}
    ]
}


def show_tree(code: str):
    tree = ast.parse(code)
    astpretty.pprint(tree)


def test_change_opt_level_w_basis_gate():

    morph, kwargs = get_mr_function_and_kwargs(
        config, metamorphic_strategy="change_opt_level")
    np.random.seed(42)
    morphed_source_code = morph("""
# SECTION
# NAME: OPTIMIZATION_PASSES

from qiskit.transpiler import PassManager
from qiskit.transpiler.passes import *
passmanager = PassManager()
qc = passmanager.run(qc)

# SECTION
# NAME: OPTIMIZATION_LEVEL

from qiskit import transpile
qc = transpile(qc, basis_gates=None, optimization_level=1)
""", **kwargs)[0]
    assert morphed_source_code == """# SECTION
# NAME: OPTIMIZATION_PASSES

from qiskit.transpiler import PassManager
from qiskit.transpiler.passes import *
passmanager = PassManager()
qc = passmanager.run(qc)
# SECTION
# NAME: OPTIMIZATION_LEVEL
from qiskit import transpile
qc = transpile(qc, basis_gates=None, optimization_level=3)
"""

