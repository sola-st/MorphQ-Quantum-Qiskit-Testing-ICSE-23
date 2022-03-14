# SECTION
# NAME: PROLOGUE

import qiskit
from qiskit import QuantumCircuit, ClassicalRegister, QuantumRegister
from qiskit.circuit.library.standard_gates import *
from qiskit.circuit import Parameter
# SECTION
# NAME: PARAMETERS

p_e3e00b = Parameter('p_e3e00b')
p_bf2884 = Parameter('p_bf2884')
p_458051 = Parameter('p_458051')
p_bea88d = Parameter('p_bea88d')
p_06fae4 = Parameter('p_06fae4')
p_f99292 = Parameter('p_f99292')
p_76436f = Parameter('p_76436f')
p_cc6879 = Parameter('p_cc6879')
p_9d7db6 = Parameter('p_9d7db6')
p_9c2d5e = Parameter('p_9c2d5e')
p_1627f7 = Parameter('p_1627f7')
p_645577 = Parameter('p_645577')
p_683d0f = Parameter('p_683d0f')
p_3d2796 = Parameter('p_3d2796')
p_3e8893 = Parameter('p_3e8893')
p_c5cbfc = Parameter('p_c5cbfc')

# SECTION
# NAME: CIRCUIT
qr = QuantumRegister(7, name='qr')
cr = ClassicalRegister(7, name='cr')
qc = QuantumCircuit(qr, cr, name='qc')
qc.append(CYGate(), qargs=[qr[0], qr[5]], cargs=[])
qc.append(RZXGate(p_e3e00b), qargs=[qr[2], qr[1]], cargs=[])
qc.append(SXdgGate(), qargs=[qr[5]], cargs=[])
qc.append(ZGate(), qargs=[qr[3]], cargs=[])
qc.append(iSwapGate(), qargs=[qr[4], qr[1]], cargs=[])
qc.append(TGate(), qargs=[qr[0]], cargs=[])
qc.append(iSwapGate(), qargs=[qr[4], qr[0]], cargs=[])
qc.append(U2Gate(p_683d0f, p_76436f), qargs=[qr[1]], cargs=[])
qc.append(CZGate(), qargs=[qr[0], qr[2]], cargs=[])
qc.append(ZGate(), qargs=[qr[5]], cargs=[])
qc.append(SXdgGate(), qargs=[qr[0]], cargs=[])
qc.append(CUGate(p_cc6879, p_1627f7, p_06fae4, p_bea88d), qargs=[qr[5], qr[
    1]], cargs=[])
qc.append(U2Gate(p_645577, p_9d7db6), qargs=[qr[5]], cargs=[])
qc.append(SwapGate(), qargs=[qr[2], qr[3]], cargs=[])
qc.append(ZGate(), qargs=[qr[3]], cargs=[])
qc.append(SwapGate(), qargs=[qr[1], qr[3]], cargs=[])
qc.append(CYGate(), qargs=[qr[0], qr[4]], cargs=[])
qc.append(U2Gate(p_c5cbfc, p_f99292), qargs=[qr[6]], cargs=[])
qc.append(SXdgGate(), qargs=[qr[2]], cargs=[])
qc.append(SXdgGate(), qargs=[qr[0]], cargs=[])
qc.append(iSwapGate(), qargs=[qr[3], qr[5]], cargs=[])
qc.append(IGate(), qargs=[qr[5]], cargs=[])
qc.append(iSwapGate(), qargs=[qr[4], qr[6]], cargs=[])
qc.append(RXXGate(p_3e8893), qargs=[qr[4], qr[5]], cargs=[])
qc.append(U1Gate(p_3d2796), qargs=[qr[5]], cargs=[])
qc.append(UGate(p_bf2884, p_458051, p_9c2d5e), qargs=[qr[2]], cargs=[])
# SECTION
# NAME: MEASUREMENT

qc.measure(qr, cr)
# SECTION
# NAME: PARAMETER_BINDING

qc = qc.bind_parameters({p_e3e00b: 5.367193223678202, p_bf2884: 2.618885683275457, p_458051: 2.0551785902896875, p_bea88d: 4.9975647700557175, p_06fae4: 4.699164921947906, p_f99292: 0.8003994976137848, p_76436f: 3.136394307849355, p_cc6879: 0.43777347012468915, p_9d7db6: 0.7288290190867878, p_9c2d5e: 0.7578066090301554, p_1627f7: 5.68369954831571, p_645577: 3.632193859157636, p_683d0f: 1.1262244236677759, p_3d2796: 6.161645337719311, p_3e8893: 3.2633407963987695,
    p_c5cbfc: 4.7030548039276825,
})

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
