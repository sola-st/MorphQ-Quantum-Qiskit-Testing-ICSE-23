import pytest
from lib.mr.inject_parameters import InjectParameters


@pytest.fixture
def transformation():
    metamorphic_strategies_config = {
        'InjectParameters': {'min_n_params': 1, 'max_n_params': 3}
    }
    detectors_config = [
        {
            'name': 'ks',
            'test_long_name': 'Kolmogorov–Smirnov Test',
            'detector_object': 'KS_Detector'
        }
    ]
    return InjectParameters(
        name="InjectParameters",
        metamorphic_strategies_config=metamorphic_strategies_config,
        detectors_config=detectors_config
    )


# def test_check_precondition_no_concrete_values(transformation):
#     """Test precondition returns False when no concrete gate parameters exist"""
#     code = """
# # SECTION
# # NAME: CIRCUIT
# qr = QuantumRegister(2)
# qc = QuantumCircuit(qr)
# qc.h(qr[0])

# # SECTION
# # NAME: EXECUTION
# job = execute(qc, backend)
# """
#     assert not transformation.check_precondition(code)


def test_check_precondition_with_concrete_values(transformation):
    """Test precondition returns True when concrete gate parameters exist"""
    code = """
# SECTION
# NAME: CIRCUIT
qr = QuantumRegister(4, name='qr')
cr = ClassicalRegister(4, name='cr')
qc = QuantumCircuit(qr, cr, name='qc')
qc.append(HGate(), qargs=[qr[1]], cargs=[])
qc.append(CRXGate(0.8166666747997124), qargs=[qr[3], qr[1]], cargs=[])

# SECTION
# NAME: EXECUTION

from qiskit_aer import AerSimulator
from qiskit_ibm_runtime import SamplerV2 as Sampler
from qiskit import transpile
backend_e76d71b0a59a4fb6bca6132418a405ed = AerSimulator(method='automatic')
sampler = Sampler(mode=backend_e76d71b0a59a4fb6bca6132418a405ed)
qc = transpile(qc, backend=backend_e76d71b0a59a4fb6bca6132418a405ed)
job = sampler.run([qc], shots=692)
counts, qc = job.result()[0].data['cr'].get_counts(), qc
RESULT = counts
"""
    assert transformation.check_precondition(code)


# def test_check_precondition_multiple_executions(transformation):
#     """Test precondition returns False when multiple execute() calls exist"""
#     code = """
# # SECTION
# # NAME: CIRCUIT
# qr = QuantumRegister(2)
# qc = QuantumCircuit(qr)
# qc.rz(0.5, qr[0])

# # SECTION
# # NAME: EXECUTION
# job1 = execute(qc, backend)
# job2 = execute(qc, backend)
# """
#     assert not transformation.check_precondition(code)
