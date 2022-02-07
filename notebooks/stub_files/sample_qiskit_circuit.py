# SECTION
# NAME: PROLOGUE
from qiskit import QuantumCircuit, ClassicalRegister, QuantumRegister

# SECTION
# NAME: CIRCUIT
qr_0 = QuantumRegister(2)
c_0 = QuantumCircuit(qr_0)

c_0.h(qr_0[0])
c_0.crz(1, qr_0[0], qr_0[1])
c_0.barrier()
c_0.id(qr_0[1])
c_0.u(1, 2, -2, qr_0[0])
c_0.u(2, 3, -2, qr_0[0])
c_0.u(3, 4, -2, qr_0[0])


# SECTION
# NAME: OPTIMIZATION

from qiskit.transpiler import PassManager
from qiskit.transpiler.passes import Optimize1qGates

passmanager = PassManager()
passmanager.append(Optimize1qGates())


# SECTION
# NAME: EXECUTION
from qiskit import Aer, transpile, execute

shots = 8192

c_0.measure_all()

backend = Aer.get_backend('qasm_simulator')
job = execute(c_0, backend=backend, shots=shots)
job_result = job.result()
count = job_result.get_counts(c_0)
print(count)

RESULT = count


# Convert to a gate and stick it into an arbitrary place in the bigger circuit
#sub_inst = sub_circ.to_instruction()

#qr = QuantumRegister(3, 'q')
#circ = QuantumCircuit(qr)
#circ.h(qr[0])
#circ.cx(qr[0], qr[1])
#circ.cx(qr[1], qr[2])
#circ.append(sub_inst, [qr[1], qr[2]])
#circ.draw()