import pytest
from lib.mr.change_qubit_order import ChangeQubitOrder
from qiskit import QuantumCircuit


@pytest.fixture
def code_of_source():
    return """
# SECTION
# NAME: CIRCUIT
qr = QuantumRegister(5, name='qr')
cr = ClassicalRegister(5, name='cr')
qc = QuantumCircuit(qr, cr, name='qc')
qc.append(XGate(), qargs=[qr[0]], cargs=[])
"""


@pytest.fixture
def transformation():
    metamorphic_strategies_config = {
        'ChangeQubitOrder': {'scramble_percentage': 0.75}}
    detectors_config = [
        {
            'name': 'ks',
            'test_long_name': 'Kolmogorov–Smirnov Test',
            'detector_object': 'KS_Detector'
        }
    ]
    return ChangeQubitOrder(
        name="ChangeQubitOrder",
        metamorphic_strategies_config=metamorphic_strategies_config,
        detectors_config=detectors_config,
        seed=4  # seed for reproducibility
        # generates {0: 3, 1: 1, 3: 0} mapping
    )


def test_derive(code_of_source, transformation):
    """Test the derive method to ensure it scrambles qubit order correctly."""
    derived_code = transformation.derive(code_of_source)
    assert "qr[0]" not in derived_code and "qr[3]" in derived_code, "The qubit order should be scrambled, qubit 0 should be mapped to qubit 3"


def test_check_output_relationship(transformation):
    """Test that check_output_relationship correctly detects equivalence."""
    # IMPORTANT: the zero index is the last digit in the bitstring
    transformation.full_mapping = {0: 0, 1: 4, 2: 2, 3: 3, 4: 1}
    result_a = {"00010": 100}
    result_b = {"10000": 100}
    test_result = transformation.check_output_relationship(result_a, result_b)
    assert int(test_result['ks']['statistic']
               ) == 0, "KS statistic should be 0 because the two results are equivalent."


def test_read_str_with_mapping(transformation):
    """Test that _read_str_with_mapping correctly maps bitstrings."""
    direct_mapping = {0: 1, 1: 0, 2: 2}
    # IMPORTANT: the zero index is the last digit in the bitstring

    # the first in the string, is the position 2 in the mapping
    # so it remains the same
    bitstring = "100"
    assert transformation._read_str_with_mapping(
        bitstring, direct_mapping) == "100"

    # the last in the string, is the position 0 in the mapping
    # so it gets mapped to 1
    assert transformation._read_str_with_mapping(
        "001", direct_mapping) == "010"
