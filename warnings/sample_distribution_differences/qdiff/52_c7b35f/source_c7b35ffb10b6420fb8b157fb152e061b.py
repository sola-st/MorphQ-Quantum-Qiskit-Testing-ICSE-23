
# SECTION
# NAME: PROLOGUE

import qiskit
from qiskit import QuantumCircuit, ClassicalRegister, QuantumRegister
from qiskit.circuit.library.standard_gates import *
from qiskit.circuit import Parameter

# SECTION
# NAME: CIRCUIT

qr = QuantumRegister(9, name='qr')
cr = ClassicalRegister(9, name='cr')
qc = QuantumCircuit(qr, cr, name='qc')
qc.append(CUGate(1.4006987211512518,5.87171748222823,1.6118094341214977,3.48470543480054), qargs=[qr[5], qr[3]], cargs=[])
qc.append(U2Gate(0.49960530614896387,3.4965748481666385), qargs=[qr[0]], cargs=[])
qc.append(iSwapGate(), qargs=[qr[5], qr[1]], cargs=[])
qc.append(RC3XGate(), qargs=[qr[1], qr[8], qr[0], qr[2]], cargs=[])
qc.append(CRYGate(4.258547097390385), qargs=[qr[5], qr[2]], cargs=[])
qc.append(PhaseGate(2.3677386437434818), qargs=[qr[1]], cargs=[])
qc.append(RYGate(3.4959547081113205), qargs=[qr[8]], cargs=[])
qc.append(RYGate(2.8331430667827977), qargs=[qr[4]], cargs=[])
qc.append(RZGate(5.34735288417693), qargs=[qr[6]], cargs=[])
qc.append(CRYGate(1.9836175804480751), qargs=[qr[5], qr[8]], cargs=[])
qc.append(CU1Gate(4.388257530988808), qargs=[qr[3], qr[4]], cargs=[])
qc.append(CUGate(2.945697832726557,3.322311684185455,2.468007457013939,1.7221796439586554), qargs=[qr[8], qr[6]], cargs=[])
qc.append(RC3XGate(), qargs=[qr[3], qr[6], qr[8], qr[5]], cargs=[])
qc.append(CYGate(), qargs=[qr[4], qr[0]], cargs=[])
qc.append(RXXGate(3.9517064865019407), qargs=[qr[7], qr[1]], cargs=[])
qc.append(RZGate(4.523490424045094), qargs=[qr[4]], cargs=[])
qc.append(RXXGate(1.4895817613653266), qargs=[qr[3], qr[1]], cargs=[])
qc.append(C3XGate(3.656036398651311), qargs=[qr[8], qr[7], qr[3], qr[5]], cargs=[])
qc.append(RXXGate(1.292848801067894), qargs=[qr[3], qr[5]], cargs=[])
qc.append(CSXGate(), qargs=[qr[8], qr[2]], cargs=[])
qc.append(CU1Gate(5.118040752270066), qargs=[qr[5], qr[3]], cargs=[])
qc.append(CSXGate(), qargs=[qr[3], qr[8]], cargs=[])
qc.append(CCXGate(), qargs=[qr[5], qr[1], qr[8]], cargs=[])
qc.append(U2Gate(2.72461573900708,2.124100420188804), qargs=[qr[7]], cargs=[])
qc.append(RZXGate(3.906832070781019), qargs=[qr[5], qr[2]], cargs=[])
qc.append(RXXGate(2.7782596144211196), qargs=[qr[2], qr[6]], cargs=[])
qc.append(CHGate(), qargs=[qr[3], qr[1]], cargs=[])
qc.append(RYGate(5.950827472980619), qargs=[qr[3]], cargs=[])

# SECTION
# NAME: MEASUREMENT

qc.measure(qr, cr)

# SECTION
# NAME: OPTIMIZATION_LEVEL

from qiskit import transpile
qc = transpile(qc, basis_gates=None, optimization_level=2, coupling_map=None)

# SECTION
# NAME: EXECUTION

from qiskit import Aer, transpile, execute
backend_b50984226d74495a9314e851a31a8441 = Aer.get_backend('qasm_simulator')
counts = execute(qc, backend=backend_b50984226d74495a9314e851a31a8441, shots=3919).result().get_counts(qc)
RESULT = counts