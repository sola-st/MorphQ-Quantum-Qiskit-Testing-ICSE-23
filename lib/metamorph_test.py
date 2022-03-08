
import pytest
import ast
import astpretty
from qmt import get_mr_function_and_kwargs
from metamorph import *
from metamorph import get_circuits_used

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


def test_extraction_of_circuits_used():
    expected_registers = [
        {'name': 'qc_main',
         'quantum_register': 'qr_main',
         'classical_register': 'cr_main',
         'size': 10},
        {'name': 'qc_1',
         'quantum_register': 'qr_1',
         'classical_register': 'cr_1',
         'size': 2},
        {'name': 'qc_2',
         'quantum_register': 'qr_2',
         'classical_register': 'cr_2',
         'size': 8}
    ]
    registers = get_circuits_used("""
qr_main = QuantumRegister(10, name='qr_main')
cr_main = ClassicalRegister(10, name='cr_main')
qc_main = QuantumCircuit(qr_main, cr_main, name='qc_main')

qr_1 = QuantumRegister(2, name='qr_1')
cr_1 = ClassicalRegister(2, name='cr_1')
qc_1 = QuantumCircuit(qr_1, cr_1, name='qc_1')
qc_1.append(SdgGate(), qargs=[qr_1[0]], cargs=[])
qc_1.append(XGate(), qargs=[qr_1[0]], cargs=[])
qc_1.append(RZZGate(0.4429181854627117), qargs=[qr_1[1], qr_1[0]], cargs=[])
qc_1.append(RYYGate(2.2725577430206263), qargs=[qr_1[0], qr_1[1]], cargs=[])
qc_1.append(TGate(), qargs=[qr_1[0]], cargs=[])

qr_2 = QuantumRegister(8, name='qr_2')
cr_2 = ClassicalRegister(8, name='cr_2')
qc_2 = QuantumCircuit(qr_2, cr_2, name='qc_2')
qc_2.append(CSXGate(), qargs=[qr_2[0], qr_2[4]], cargs=[])
qc_2.append(HGate(), qargs=[qr_2[1]], cargs=[])
qc_2.append(CSXGate(), qargs=[qr_2[6], qr_2[1]], cargs=[])
qc_2.append(CRXGate(4.017627836736385), qargs=[qr_2[4], qr_2[2]], cargs=[])
qc_2.append(RZGate(5.914588166120627), qargs=[qr_2[6]], cargs=[])

qc_main.append(qc_1, qargs=qr_main[:2], cargs=cr_main[:2])
qc_main.append(qc_2, qargs=qr_main[2:], cargs=cr_main[2:])
qc_main.draw(fold=-1)
""")
    for register in expected_registers:
        assert register in registers
    for register in registers:
        assert register in expected_registers


def test_check_backend_presence_found():
    res = check_function_call_in_code(source_code="""from qiskit import Aer, transpile, execute
backend_6b62557ac33843e7a8245322cae17865 = Aer.get_backend('qasm_simulator')
counts = execute(qc, backend=backend_6b62557ac33843e7a8245322cae17865, shots=692).result().get_counts(qc)
RESULT = counts""", func_name="get_backend")
    assert res, "The code analysis doesn't recognize get_backend API"


def test_check_backend_presence_not_found():
    res = check_function_call_in_code(source_code="""from qiskit import transpile
qc = transpile(qc, basis_gates=None, optimization_level=3, coupling_map=None)""", func_name="get_backend")
    assert not res, "The code analysis recognize get_backend API where there is not"


def test_check_transpile_presence_not_found():
    res = check_function_call_in_code(source_code="""from qiskit import Aer, transpile, execute
backend_6b62557ac33843e7a8245322cae17865 = Aer.get_backend('qasm_simulator')
counts = execute(qc, backend=backend_6b62557ac33843e7a8245322cae17865, shots=692).result().get_counts(qc)
RESULT = counts""", func_name="transpile")
    assert not res, "The code analysis recognize transpile API where there is not"


def test_check_transpile_presence_found():
    res = check_function_call_in_code(source_code="""from qiskit import transpile
qc = transpile(qc, basis_gates=None, optimization_level=3, coupling_map=None)""", func_name="transpile")
    assert res, "The code analysis doesn't recognize transpile API"


def test_cluster_of_qubit_when_possible():
    res = cluster_qubits(circuit_code="""qr_1 = QuantumRegister(3, name='qr_1')
cr_1 = ClassicalRegister(3, name='cr_1')
qc_1 = QuantumCircuit(qr_1, cr_1, name='qc_1')
qc_1.append(SdgGate(), qargs=[qr_1[0]], cargs=[])
qc_1.append(XGate(), qargs=[qr_1[0]], cargs=[])
qc_1.append(RZZGate(0.4429181854627117), qargs=[qr_1[1], qr_1[0]], cargs=[])
qc_1.append(RYYGate(2.2725577430206263), qargs=[qr_1[0], qr_1[1]], cargs=[])
qc_1.append(TGate(), qargs=[qr_1[0]], cargs=[])
qc_1.append(XGate(), qargs=[qr_1[2]], cargs=[])""",
    circuit_name="qc_1", register_name="qr_1")
    assert res == {frozenset({2}), frozenset({0, 1})}


def test_extract_instructions():
    res = get_instructions("""
qc_2.append(RZXGate(2.5674333, p_29392d), qargs=[qr_2[2], qr_2[1]], cargs=[])
qc_1.append(CUGate(p_a7c416, p_53f0d4, 1.1382126210061985, p_b2bdc1), qargs
    =[qr_1[4], qr_1[3]], cargs=[])""")
    assert res == [
        {
            "circuit_id": "qc_2",
            "gate": "RZXGate",
            "params": [2.5674333, "p_29392d"],
            "qregs": ["qr_2", "qr_2"],
            "qbits": [2, 1],
            "cregs": [],
            "cbits": [],
            'code': 'qc_2.append(RZXGate(2.5674333, p_29392d), qargs=[qr_2[2], qr_2[1]], cargs=[])'
        },
        {
            "circuit_id": "qc_1",
            "gate": "CUGate",
            "params": ["p_a7c416", "p_53f0d4", 1.1382126210061985, "p_b2bdc1"],
            "qregs": ["qr_1", "qr_1"],
            "qbits": [4, 3],
            "cregs": [],
            "cbits": [],
            'code': 'qc_1.append(CUGate(p_a7c416, p_53f0d4, 1.1382126210061985, p_b2bdc1), qargs =[qr_1[4], qr_1[3]], cargs=[])'
        }
    ]
