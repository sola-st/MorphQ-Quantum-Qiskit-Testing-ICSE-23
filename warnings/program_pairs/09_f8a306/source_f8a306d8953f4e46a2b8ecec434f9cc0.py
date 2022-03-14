
# SECTION
# NAME: PROLOGUE

import qiskit
from qiskit import QuantumCircuit, ClassicalRegister, QuantumRegister
from qiskit.circuit.library.standard_gates import *
from qiskit.circuit import Parameter

# SECTION
# NAME: CIRCUIT

qr = QuantumRegister(7, name='qr')
cr = ClassicalRegister(7, name='cr')
qc = QuantumCircuit(qr, cr, name='qc')
qc.append(CYGate(), qargs=[qr[0], qr[5]], cargs=[])
qc.append(RZXGate(5.367193223678202), qargs=[qr[2], qr[1]], cargs=[])
qc.append(SXdgGate(), qargs=[qr[5]], cargs=[])
qc.append(ZGate(), qargs=[qr[3]], cargs=[])
qc.append(iSwapGate(), qargs=[qr[4], qr[1]], cargs=[])
qc.append(TGate(), qargs=[qr[0]], cargs=[])
qc.append(iSwapGate(), qargs=[qr[4], qr[0]], cargs=[])
qc.append(U2Gate(1.1262244236677759,3.136394307849355), qargs=[qr[1]], cargs=[])
qc.append(CZGate(), qargs=[qr[0], qr[2]], cargs=[])
qc.append(ZGate(), qargs=[qr[5]], cargs=[])
qc.append(SXdgGate(), qargs=[qr[0]], cargs=[])
qc.append(CUGate(0.43777347012468915,5.68369954831571,4.699164921947906,4.9975647700557175), qargs=[qr[5], qr[1]], cargs=[])
qc.append(U2Gate(3.632193859157636,0.7288290190867878), qargs=[qr[5]], cargs=[])
qc.append(SwapGate(), qargs=[qr[2], qr[3]], cargs=[])
qc.append(ZGate(), qargs=[qr[3]], cargs=[])
qc.append(SwapGate(), qargs=[qr[1], qr[3]], cargs=[])
qc.append(CYGate(), qargs=[qr[0], qr[4]], cargs=[])
qc.append(U2Gate(4.7030548039276825,0.8003994976137848), qargs=[qr[6]], cargs=[])
qc.append(SXdgGate(), qargs=[qr[2]], cargs=[])
qc.append(SXdgGate(), qargs=[qr[0]], cargs=[])
qc.append(iSwapGate(), qargs=[qr[3], qr[5]], cargs=[])
qc.append(IGate(), qargs=[qr[5]], cargs=[])
qc.append(iSwapGate(), qargs=[qr[4], qr[6]], cargs=[])
qc.append(RXXGate(3.2633407963987695), qargs=[qr[4], qr[5]], cargs=[])
qc.append(U1Gate(6.161645337719311), qargs=[qr[5]], cargs=[])
qc.append(UGate(2.618885683275457,2.0551785902896875,0.7578066090301554), qargs=[qr[2]], cargs=[])

# SECTION
# NAME: MEASUREMENT

qc.measure(qr, cr)

# SECTION
# NAME: OPTIMIZATION_PASSES

from qiskit.transpiler import PassManager
from qiskit.transpiler.passes import *
passmanager = PassManager()
qc = passmanager.run(qc)

# SECTION
# NAME: OPTIMIZATION_LEVEL

from qiskit import transpile
qc = transpile(qc, basis_gates=None, optimization_level=0, coupling_map=None)

# SECTION
# NAME: EXECUTION

from qiskit import Aer, transpile, execute
backend_90bf2621236540029b91a1befca7360e = Aer.get_backend('qasm_simulator')
counts = execute(qc, backend=backend_90bf2621236540029b91a1befca7360e, shots=1959).result().get_counts(qc)
RESULT = counts