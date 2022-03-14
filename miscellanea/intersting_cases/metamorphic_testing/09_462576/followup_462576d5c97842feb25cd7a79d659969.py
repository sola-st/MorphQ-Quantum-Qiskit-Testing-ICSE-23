# SECTION
# NAME: PROLOGUE

import qiskit
from qiskit import QuantumCircuit, ClassicalRegister, QuantumRegister
from qiskit.circuit.library.standard_gates import *
from qiskit.circuit import Parameter
# SECTION
# NAME: PARAMETERS
# SECTION
# NAME: PARAMETERS
p_635ba3 = Parameter('p_635ba3')
p_fae9fb = Parameter('p_fae9fb')
p_57350f = Parameter('p_57350f')
p_e7a107 = Parameter('p_e7a107')
p_2a349d = Parameter('p_2a349d')
p_66bb34 = Parameter('p_66bb34')
p_a14f4b = Parameter('p_a14f4b')
p_fc847c = Parameter('p_fc847c')
p_5e95c0 = Parameter('p_5e95c0')
p_ead18a = Parameter('p_ead18a')
p_ea6b6f = Parameter('p_ea6b6f')
p_25b26e = Parameter('p_25b26e')
p_3bc0e6 = Parameter('p_3bc0e6')
p_4978fb = Parameter('p_4978fb')
p_0d7222 = Parameter('p_0d7222')
p_1c65da = Parameter('p_1c65da')
p_59eb9a = Parameter('p_59eb9a')
p_f7570d = Parameter('p_f7570d')
p_28612d = Parameter('p_28612d')

# SECTION
# NAME: CIRCUIT
qr = QuantumRegister(8, name='qr')
cr = ClassicalRegister(8, name='cr')
qc = QuantumCircuit(qr, cr, name='qc')
qc.append(RC3XGate(), qargs=[qr[5], qr[4], qr[7], qr[0]], cargs=[])
qc.append(RYGate(p_28612d), qargs=[qr[6]], cargs=[])
qc.append(CPhaseGate(p_4978fb), qargs=[qr[4], qr[6]], cargs=[])
qc.append(SXdgGate(), qargs=[qr[4]], cargs=[])
qc.append(ZGate(), qargs=[qr[7]], cargs=[])
qc.append(SXdgGate(), qargs=[qr[6]], cargs=[])
qc.append(C4XGate(), qargs=[qr[0], qr[4], qr[2], qr[3], qr[1]], cargs=[])
qc.append(SXGate(), qargs=[qr[5]], cargs=[])
qc.append(CU3Gate(p_1c65da, p_e7a107, p_0d7222), qargs=[qr[7], qr[2]], cargs=[]
    )
qc.append(XGate(), qargs=[qr[4]], cargs=[])
qc.append(iSwapGate(), qargs=[qr[6], qr[0]], cargs=[])
qc.append(CYGate(), qargs=[qr[7], qr[5]], cargs=[])
qc.append(RYGate(p_ea6b6f), qargs=[qr[3]], cargs=[])
qc.append(SXdgGate(), qargs=[qr[6]], cargs=[])
qc.append(CSXGate(), qargs=[qr[4], qr[2]], cargs=[])
qc.append(XGate(), qargs=[qr[7]], cargs=[])
qc.append(PhaseGate(1.2438266115605516), qargs=[qr[7]], cargs=[])
qc.append(SXGate(), qargs=[qr[0]], cargs=[])
qc.append(UGate(p_59eb9a, p_57350f, p_f7570d), qargs=[qr[2]], cargs=[])
qc.append(UGate(p_fc847c, p_25b26e, p_66bb34), qargs=[qr[3]], cargs=[])
qc.append(C3XGate(p_ead18a), qargs=[qr[7], qr[2], qr[4], qr[3]], cargs=[])
qc.append(ZGate(), qargs=[qr[7]], cargs=[])
qc.append(CYGate(), qargs=[qr[3], qr[4]], cargs=[])
qc.append(CPhaseGate(p_5e95c0), qargs=[qr[6], qr[7]], cargs=[])
qc.append(C4XGate(), qargs=[qr[3], qr[5], qr[0], qr[6], qr[4]], cargs=[])
qc.append(U3Gate(p_fae9fb, p_635ba3, 0.9258326441720094), qargs=[qr[6]],
    cargs=[])
qc.append(UGate(p_3bc0e6, p_2a349d, p_a14f4b), qargs=[qr[2]], cargs=[])
qc.append(XGate(), qargs=[qr[5]], cargs=[])
# SECTION
# NAME: MEASUREMENT

qc.measure(qr, cr)
# SECTION
# NAME: PARAMETER_BINDING

qc = qc.bind_parameters({
    p_635ba3: 0.8995363765101827,
    p_fae9fb: 3.93259544543144,
    p_57350f: 6.151167587061927,
    p_e7a107: 2.031963053978228,
    p_2a349d: 1.041601853524223,
    p_66bb34: 5.447933987599033,
    p_a14f4b: 3.356938865229232,
    p_fc847c: 6.150190310902739,
    p_5e95c0: 0.14740362211632352,
    p_ead18a: 4.684182496138248,
    p_ea6b6f: 2.9525339778910276,
    p_25b26e: 2.450261504210688,
    p_3bc0e6: 3.914387676578735,
    p_4978fb: 3.8958253680897545,
    p_0d7222: 4.115588921668292,
    p_1c65da: 5.6334380494507,
    p_59eb9a: 1.2475578981205417,
    p_f7570d: 4.766205850306024,
    p_28612d: 4.577315427580833,
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
qc = transpile(qc, basis_gates=None, optimization_level=2, coupling_map=None)
# SECTION
# NAME: EXECUTION

from qiskit import Aer, transpile, execute
backend_7e67d8ab8ef944f9ba7f1e056f79a182 = Aer.get_backend('qasm_simulator')
counts = execute(qc, backend=backend_7e67d8ab8ef944f9ba7f1e056f79a182, shots=2771).result().get_counts(qc)
RESULT = counts
