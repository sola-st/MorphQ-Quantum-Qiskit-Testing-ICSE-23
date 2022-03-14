
# SECTION
# NAME: PROLOGUE

import qiskit
from qiskit import QuantumCircuit, ClassicalRegister, QuantumRegister
from qiskit.circuit.library.standard_gates import *

# SECTION
# NAME: CIRCUIT

qr = QuantumRegister(3, name='qr')
cr = ClassicalRegister(3, name='cr')
qc = QuantumCircuit(qr, cr, name='qc')
qc.append(CHGate(), qargs=[qr[0], qr[2]], cargs=[])
qc.append(DCXGate(), qargs=[qr[1], qr[0]], cargs=[])
qc.append(CSwapGate(), qargs=[qr[0], qr[1], qr[2]], cargs=[])
qc.append(SwapGate(), qargs=[qr[0], qr[2]], cargs=[])
qc.append(SwapGate(), qargs=[qr[0], qr[2]], cargs=[])
qc.append(U3Gate(3.1333796742925704,2.0782915724294266,3.8528667493673407), qargs=[qr[0]], cargs=[])
qc.append(XGate(), qargs=[qr[0]], cargs=[])
qc.append(XGate(), qargs=[qr[1]], cargs=[])
qc.append(UGate(3.2932004434738897,4.615954301356511,5.807945035399611), qargs=[qr[0]], cargs=[])
qc.append(CCXGate(), qargs=[qr[1], qr[2], qr[0]], cargs=[])
qc.append(CU3Gate(0.9780797026556811,2.5266379849635308,5.799484270194845), qargs=[qr[2], qr[1]], cargs=[])
qc.append(SwapGate(), qargs=[qr[0], qr[1]], cargs=[])
qc.append(SwapGate(), qargs=[qr[1], qr[2]], cargs=[])
qc.append(CHGate(), qargs=[qr[0], qr[1]], cargs=[])
qc.append(CRZGate(6.101795211804666), qargs=[qr[1], qr[2]], cargs=[])
qc.append(U3Gate(2.5199573414643814,6.119039916799916,3.381561021165288), qargs=[qr[0]], cargs=[])
qc.append(UGate(3.731686677882394,4.537227390583343,0.42149888050188145), qargs=[qr[1]], cargs=[])
qc.append(SwapGate(), qargs=[qr[0], qr[1]], cargs=[])
qc.append(RZZGate(1.2549960087029204), qargs=[qr[1], qr[0]], cargs=[])

# SECTION
# NAME: OPTIMIZATION_PASSES

from qiskit.transpiler import PassManager
from qiskit.transpiler.passes import *
passmanager = PassManager()
qc = passmanager.run(qc)

# SECTION
# NAME: OPTIMIZATION_LEVEL

from qiskit import transpile
qc = transpile(qc, basis_gates=None, optimization_level=2, coupling_map=None)

# SECTION
# NAME: MEASUREMENT

qc.measure(qr, cr)

# SECTION
# NAME: EXECUTION

from qiskit import Aer, transpile, execute
backend_98ae9f2e9e3f4728a9fa5a427cf0751b = Aer.get_backend('qasm_simulator')
counts = execute(qc, backend=backend_98ae9f2e9e3f4728a9fa5a427cf0751b, shots=489).result().get_counts(qc)
RESULT = counts