
# SECTION
# NAME: PROLOGUE

import qiskit
from qiskit import QuantumCircuit, ClassicalRegister, QuantumRegister
from qiskit.circuit.library.standard_gates import *

# SECTION
# NAME: CIRCUIT

qr = QuantumRegister(11, name='qr')
cr = ClassicalRegister(11, name='cr')
qc = QuantumCircuit(qr, cr, name='qc')
qc.append(DCXGate(), qargs=[qr[10], qr[7]], cargs=[])
qc.append(SwapGate(), qargs=[qr[4], qr[9]], cargs=[])
qc.append(RC3XGate(), qargs=[qr[4], qr[7], qr[9], qr[10]], cargs=[])
qc.append(RZZGate(1.0030234100866742), qargs=[qr[2], qr[7]], cargs=[])
qc.append(RXGate(2.4590222375857405), qargs=[qr[10]], cargs=[])
qc.append(CXGate(), qargs=[qr[2], qr[7]], cargs=[])
qc.append(CU3Gate(4.481757977946718,6.266761665568213,2.8175272958086586), qargs=[qr[1], qr[10]], cargs=[])
qc.append(RXXGate(2.9504345929880245), qargs=[qr[2], qr[4]], cargs=[])
qc.append(CZGate(), qargs=[qr[3], qr[5]], cargs=[])
qc.append(RXGate(2.4448244382563917), qargs=[qr[1]], cargs=[])
qc.append(RZZGate(0.8947394340363162), qargs=[qr[6], qr[7]], cargs=[])
qc.append(CXGate(), qargs=[qr[9], qr[1]], cargs=[])
qc.append(SGate(), qargs=[qr[3]], cargs=[])
qc.append(CUGate(4.702619501391067,2.389894295861376,2.6621743749936084,1.8786699945755476), qargs=[qr[6], qr[7]], cargs=[])
qc.append(SGate(), qargs=[qr[6]], cargs=[])
qc.append(CRZGate(0.5314832461931365), qargs=[qr[7], qr[6]], cargs=[])
qc.append(CSwapGate(), qargs=[qr[8], qr[3], qr[7]], cargs=[])
qc.append(U2Gate(5.938911748571366,5.1519809156447005), qargs=[qr[6]], cargs=[])
qc.append(PhaseGate(0.7459639210025368), qargs=[qr[5]], cargs=[])
qc.append(U3Gate(1.4779720747645735,3.8615445744041708,2.799950813574806), qargs=[qr[6]], cargs=[])
qc.append(PhaseGate(1.4169402094934866), qargs=[qr[3]], cargs=[])
qc.append(CHGate(), qargs=[qr[5], qr[7]], cargs=[])
qc.append(CUGate(1.0806678132326375,0.6835655409900315,4.550681418051636,6.030610393829874), qargs=[qr[0], qr[10]], cargs=[])
qc.append(CCXGate(), qargs=[qr[8], qr[7], qr[3]], cargs=[])

# SECTION
# NAME: OPTIMIZATION_PASSES

from qiskit.transpiler import PassManager
from qiskit.transpiler.passes import *
passmanager = PassManager()
qc = passmanager.run(qc)

# SECTION
# NAME: OPTIMIZATION_LEVEL

from qiskit import transpile
qc = transpile(qc, basis_gates=None, optimization_level=3, coupling_map=None)

# SECTION
# NAME: MEASUREMENT

qc.measure(qr, cr)

# SECTION
# NAME: EXECUTION

from qiskit import Aer, transpile, execute
backend_08b75d98ced74bc082226015d3d98c3b = Aer.get_backend('qasm_simulator')
counts = execute(qc, backend=backend_08b75d98ced74bc082226015d3d98c3b, shots=7838).result().get_counts(qc)
RESULT = counts