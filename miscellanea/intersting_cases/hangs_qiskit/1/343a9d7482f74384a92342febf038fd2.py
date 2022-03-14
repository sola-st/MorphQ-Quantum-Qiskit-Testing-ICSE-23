
# SECTION
# NAME: PROLOGUE

import qiskit
from qiskit import QuantumCircuit, ClassicalRegister, QuantumRegister
from qiskit.circuit.library.standard_gates import *

# SECTION
# NAME: CIRCUIT

qr_qr = QuantumRegister(16, name='qr_qr')
cr_qr = ClassicalRegister(16, name='cr_qr')
qc = QuantumCircuit(qr_qr, cr_qr, name='qc')
qc.append(C3XGate(3.907524998275438), qargs=[qr_qr[11], qr_qr[8], qr_qr[7], qr_qr[0]], cargs=[])
qc.append(RC3XGate(), qargs=[qr_qr[8], qr_qr[15], qr_qr[5], qr_qr[14]], cargs=[])
qc.append(CHGate(), qargs=[qr_qr[10], qr_qr[15]], cargs=[])
qc.append(CU1Gate(4.818142106647685), qargs=[qr_qr[0], qr_qr[6]], cargs=[])
qc.append(RYGate(1.0309627158294603), qargs=[qr_qr[4]], cargs=[])
qc.append(CU1Gate(5.752429763184833), qargs=[qr_qr[8], qr_qr[12]], cargs=[])
qc.append(CRZGate(2.729319301936734), qargs=[qr_qr[15], qr_qr[7]], cargs=[])
qc.append(CUGate(1.7865204421912357,2.217990729902729,5.83693248435634,2.9917879555121014), qargs=[qr_qr[1], qr_qr[0]], cargs=[])
qc.append(PhaseGate(2.924195801896616), qargs=[qr_qr[13]], cargs=[])
qc.append(SwapGate(), qargs=[qr_qr[12], qr_qr[3]], cargs=[])
qc.append(PhaseGate(3.5869222695753247), qargs=[qr_qr[7]], cargs=[])
qc.append(CRYGate(0.5425198941315491), qargs=[qr_qr[10], qr_qr[9]], cargs=[])
qc.append(CRZGate(2.6246855324310436), qargs=[qr_qr[9], qr_qr[5]], cargs=[])
qc.append(RZGate(3.5664487201467474), qargs=[qr_qr[10]], cargs=[])
qc.append(C3XGate(5.123156258149011), qargs=[qr_qr[9], qr_qr[8], qr_qr[13], qr_qr[2]], cargs=[])
qc.append(RZGate(4.063125348530302), qargs=[qr_qr[3]], cargs=[])
qc.append(RYGate(5.596839547865737), qargs=[qr_qr[2]], cargs=[])
qc.append(CRYGate(3.107299163630677), qargs=[qr_qr[4], qr_qr[5]], cargs=[])
qc.append(CHGate(), qargs=[qr_qr[14], qr_qr[0]], cargs=[])
qc.append(CRXGate(1.5360054846340931), qargs=[qr_qr[6], qr_qr[11]], cargs=[])
qc.append(PhaseGate(1.8699138522602958), qargs=[qr_qr[6]], cargs=[])
qc.append(SwapGate(), qargs=[qr_qr[2], qr_qr[15]], cargs=[])
qc.append(CRZGate(1.4596411939138862), qargs=[qr_qr[3], qr_qr[1]], cargs=[])
qc.append(CU1Gate(2.0594298214588345), qargs=[qr_qr[0], qr_qr[6]], cargs=[])
qc.append(YGate(), qargs=[qr_qr[2]], cargs=[])
qc.append(CUGate(1.736098146392435,0.3890656207668619,2.9043239431659917,1.346317026764786), qargs=[qr_qr[12], qr_qr[13]], cargs=[])
qc.append(TGate(), qargs=[qr_qr[14]], cargs=[])
qc.append(RYGate(4.549942261513976), qargs=[qr_qr[0]], cargs=[])
qc.append(iSwapGate(), qargs=[qr_qr[5], qr_qr[13]], cargs=[])
qc.append(C3XGate(3.5495149923548728), qargs=[qr_qr[12], qr_qr[14], qr_qr[9], qr_qr[7]], cargs=[])

# SECTION
# NAME: OPTIMIZATION_PASSES

from qiskit.transpiler import PassManager
from qiskit.transpiler.passes import *
passmanager = PassManager()
qc = passmanager.run(qc)

# SECTION
# NAME: OPTIMIZATION_LEVEL

from qiskit import transpile
qc = transpile(qc, basis_gates=['tdggate', 'sxdggate', 'chgate', 'rzgate', 'phasegate'], optimization_level=0)

# SECTION
# NAME: MEASUREMENT

qc.measure(qr_qr, cr_qr)

# SECTION
# NAME: EXECUTION

from qiskit import Aer, transpile, execute
backend_efb784840b7d41c9b4f9139f73da3c40 = Aer.get_backend('qasm_simulator')
RESULT = execute(qc, backend=backend_efb784840b7d41c9b4f9139f73da3c40, shots=44340).result().get_counts(qc)