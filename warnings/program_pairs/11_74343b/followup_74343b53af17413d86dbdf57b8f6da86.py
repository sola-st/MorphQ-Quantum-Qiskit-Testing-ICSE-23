# SECTION
# NAME: PROLOGUE

import qiskit
from qiskit import QuantumCircuit, ClassicalRegister, QuantumRegister
from qiskit.circuit.library.standard_gates import *
from qiskit.circuit import Parameter
# SECTION
# NAME: PARAMETERS

p_b4e18a = Parameter('p_b4e18a')
p_d6f4de = Parameter('p_d6f4de')
p_f8d5cb = Parameter('p_f8d5cb')
p_6f6798 = Parameter('p_6f6798')
p_8f1b18 = Parameter('p_8f1b18')
p_54c99b = Parameter('p_54c99b')
p_27e391 = Parameter('p_27e391')
p_9410b5 = Parameter('p_9410b5')
p_8c78e2 = Parameter('p_8c78e2')
p_53c3a2 = Parameter('p_53c3a2')
p_0643e5 = Parameter('p_0643e5')

# SECTION
# NAME: CIRCUIT
qr = QuantumRegister(7, name='qr')
cr = ClassicalRegister(7, name='cr')
qc = QuantumCircuit(qr, cr, name='qc')
qc.append(RZZGate(p_f8d5cb), qargs=[qr[5], qr[6]], cargs=[])
qc.append(CSwapGate(), qargs=[qr[6], qr[4], qr[1]], cargs=[])
qc.append(RYYGate(p_54c99b), qargs=[qr[2], qr[5]], cargs=[])
qc.append(RYYGate(p_8f1b18), qargs=[qr[0], qr[4]], cargs=[])
qc.append(iSwapGate(), qargs=[qr[3], qr[2]], cargs=[])
qc.append(ECRGate(), qargs=[qr[6], qr[0]], cargs=[])
qc.append(RZXGate(p_27e391), qargs=[qr[0], qr[6]], cargs=[])
qc.append(RYYGate(p_9410b5), qargs=[qr[3], qr[4]], cargs=[])
qc.append(CSwapGate(), qargs=[qr[1], qr[0], qr[6]], cargs=[])
qc.append(HGate(), qargs=[qr[2]], cargs=[])
qc.append(YGate(), qargs=[qr[3]], cargs=[])
qc.append(RZXGate(p_53c3a2), qargs=[qr[0], qr[1]], cargs=[])
qc.append(CRXGate(p_8c78e2), qargs=[qr[3], qr[5]], cargs=[])
qc.append(RZXGate(p_b4e18a), qargs=[qr[1], qr[3]], cargs=[])
qc.append(RXGate(p_0643e5), qargs=[qr[0]], cargs=[])
qc.append(TGate(), qargs=[qr[5]], cargs=[])
qc.append(CSwapGate(), qargs=[qr[2], qr[5], qr[0]], cargs=[])
qc.append(SdgGate(), qargs=[qr[0]], cargs=[])
qc.append(RXGate(p_6f6798), qargs=[qr[3]], cargs=[])
qc.append(SdgGate(), qargs=[qr[5]], cargs=[])
qc.append(CHGate(), qargs=[qr[6], qr[5]], cargs=[])
qc.append(iSwapGate(), qargs=[qr[2], qr[1]], cargs=[])
qc.append(RXGate(p_d6f4de), qargs=[qr[5]], cargs=[])
# SECTION
# NAME: MEASUREMENT

qc.measure(qr, cr)
# SECTION
# NAME: PARAMETER_BINDING

qc = qc.bind_parameters({p_b4e18a: 5.750557455994805, p_d6f4de: 0.041239490820221554, p_f8d5cb: 2.0549471012132114, p_6f6798: 5.773025482276404, p_8f1b18: 1.7784823832136227, p_54c99b: 4.549715767353061, p_27e391: 1.7009764849793279, p_9410b5: 0.8783624118527082, p_8c78e2: 3.456774343949486, p_53c3a2: 4.626516799242062,
    p_0643e5: 4.810686391845515,
})

# SECTION
# NAME: OPTIMIZATION_LEVEL

from qiskit import transpile
qc = transpile(qc, basis_gates=None, optimization_level=2, coupling_map=None)
# SECTION
# NAME: QASM_CONVERTION

qc = QuantumCircuit.from_qasm_str(qc.qasm())
# SECTION
# NAME: EXECUTION

from qiskit import Aer, transpile, execute
backend_e5edeb491b5e49f59d37b5d841e91f7e = Aer.get_backend('qasm_simulator')
counts = execute(qc, backend=backend_e5edeb491b5e49f59d37b5d841e91f7e, shots=1959).result().get_counts(qc)
RESULT = counts
