
# SECTION
# NAME: PROLOGUE

import qiskit
from qiskit import QuantumCircuit, ClassicalRegister, QuantumRegister
from qiskit.circuit.library.standard_gates import *
from qiskit.circuit import Parameter

# SECTION
# NAME: CIRCUIT

qr = QuantumRegister(4, name='qr')
cr = ClassicalRegister(4, name='cr')
qc = QuantumCircuit(qr, cr, name='qc')
qc.append(CUGate(1.4006987211512518,5.87171748222823,1.6118094341214977,3.48470543480054), qargs=[qr[2], qr[1]], cargs=[])
qc.append(CUGate(1.1871631023192395,3.1208310247400375,4.6969093516914615,0.17758444859871442), qargs=[qr[2], qr[0]], cargs=[])
qc.append(CRYGate(0.6970696680696589), qargs=[qr[0], qr[1]], cargs=[])
qc.append(CSwapGate(), qargs=[qr[0], qr[3], qr[1]], cargs=[])
qc.append(RYGate(1.6125723299807893), qargs=[qr[1]], cargs=[])
qc.append(ZGate(), qargs=[qr[0]], cargs=[])
qc.append(TGate(), qargs=[qr[3]], cargs=[])
qc.append(RC3XGate(), qargs=[qr[0], qr[1], qr[2], qr[3]], cargs=[])
qc.append(C3XGate(5.748870687038669), qargs=[qr[1], qr[2], qr[0], qr[3]], cargs=[])
qc.append(CRYGate(4.258547097390385), qargs=[qr[3], qr[1]], cargs=[])
qc.append(RYGate(5.620914585085149), qargs=[qr[3]], cargs=[])
qc.append(PhaseGate(2.3677386437434818), qargs=[qr[3]], cargs=[])
qc.append(RYGate(1.8882312521616809), qargs=[qr[1]], cargs=[])
qc.append(RYGate(3.4959547081113205), qargs=[qr[3]], cargs=[])
qc.append(RYGate(5.99120670299654), qargs=[qr[3]], cargs=[])
qc.append(iSwapGate(), qargs=[qr[1], qr[2]], cargs=[])
qc.append(CUGate(5.709276284014425,1.1243723913896708,5.481400346001526,3.157375188814291), qargs=[qr[0], qr[1]], cargs=[])
qc.append(PhaseGate(4.139653233556392), qargs=[qr[3]], cargs=[])
qc.append(CRYGate(1.9836175804480751), qargs=[qr[3], qr[2]], cargs=[])
qc.append(CSwapGate(), qargs=[qr[3], qr[0], qr[2]], cargs=[])
qc.append(U2Gate(2.0386602682603954,6.248470925834253), qargs=[qr[3]], cargs=[])
qc.append(C3XGate(5.136329093347736), qargs=[qr[3], qr[1], qr[0], qr[2]], cargs=[])

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
backend_9efd76d3583849389d023ab4ac20c470 = Aer.get_backend('qasm_simulator')
counts = execute(qc, backend=backend_9efd76d3583849389d023ab4ac20c470, shots=692).result().get_counts(qc)
RESULT = counts