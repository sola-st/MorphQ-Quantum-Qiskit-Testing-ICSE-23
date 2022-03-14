I the binding of parameters in the CUGate doesn't work as expected.
If I parametrize a circuit with CUGate and I bind any of its parameters via `bind_parameters` before running it, it fails with the following error: `Mismatch between run_config.parameter_binds and all circuit parameters. Parameter binds: [] Circuit parameters: [ParameterView([Parameter(a)])]`.


Running the following circuit:
```python
import qiskit
from qiskit import QuantumCircuit, ClassicalRegister, QuantumRegister
from qiskit.circuit.library.standard_gates import *
from qiskit.circuit import Parameter
from math import pi

a = Parameter('a')

qr = QuantumRegister(2, name='qr')
cr = ClassicalRegister(2, name='cr')
qc = QuantumCircuit(qr, cr, name='qc')
qc.append(CUGate(a, pi, pi, pi), qargs=[qr[0], qr[1]], cargs=[])
qc.measure(qr, cr)
qc.draw(fold=-1)
```
```python
                    ┌─┐
qr_0: ──────■───────┤M├───
      ┌─────┴──────┐└╥┘┌─┐
qr_1: ┤ U(a,π,π,π) ├─╫─┤M├
      └────────────┘ ║ └╥┘
cr: 2/═══════════════╩══╩═
                     0  1
```

Then we bind the parameter `a` to `pi`. And run it.
```python
qc = qc.bind_parameters({
    a: pi,
})

from qiskit import Aer, transpile, execute
backend = Aer.get_backend('qasm_simulator')
job = backend.run(transpile(qc, backend))
counts = job.result().get_counts()
counts
```
Output:
```python
QiskitError                               Traceback (most recent call last)
/tmp/ipykernel_35760/3208503948.py in <module>
      5 from qiskit import Aer, transpile, execute
      6 backend = Aer.get_backend('qasm_simulator')
----> 7 job = backend.run(transpile(qc, backend))
      8 counts = job.result().get_counts()
      9 counts

qiskit/utils/deprecation.py in wrapper(*args, **kwargs)
     25             if kwargs:
     26                 _rename_kwargs(func.__name__, kwargs, kwarg_map)
---> 27             return func(*args, **kwargs)
     28
     29         return wrapper

qiskit/providers/aer/backends/aerbackend.py in run(self, circuits, validate, parameter_binds, **run_options)
    206             qobj = self._assemble(circuits, **run_options)
    207         else:
--> 208             qobj = self._assemble(circuits, parameter_binds=parameter_binds, **run_options)
    209
    210         # Optional validation

qiskit/providers/aer/backends/aerbackend.py in _assemble(self, circuits, parameter_binds, **run_options)
    352                             parameterizations=parameterizations)
    353         else:
--> 354             qobj = assemble(circuits, self)
    355
    356         # Add options

qiskit/compiler/assembler.py in assemble(experiments, backend, qobj_id, qobj_header, shots, memory, max_credits, seed_simulator, qubit_lo_freq, meas_lo_freq, qubit_lo_range, meas_lo_range, schedule_los, meas_level, meas_return, meas_map, memory_slot_size, rep_time, rep_delay, parameter_binds, parametric_pulses, init_qubits, **run_config)
    190
    191         # If circuits are parameterized, bind parameters and remove from run_config
--> 192         bound_experiments, run_config = _expand_parameters(
    193             circuits=experiments, run_config=run_config
    194         )

qiskit/compiler/assembler.py in _expand_parameters(circuits, run_config)
    581             or any(unique_parameters != parameters for parameters in all_circuit_parameters)
    582         ):
--> 583             raise QiskitError(
    584                 (
    585                     "Mismatch between run_config.parameter_binds and all circuit parameters. "

QiskitError: 'Mismatch between run_config.parameter_binds and all circuit parameters. Parameter binds: [] Circuit parameters: [ParameterView([Parameter(a)])]'
```
It fails, and it does so also with other parameters and/or other float values.



The circuit should bind the parameter `a`, return a runnable circuit and give me the result of this runnable circuit.


It seems to be a particularity of the CUGate whenever it has parameters.