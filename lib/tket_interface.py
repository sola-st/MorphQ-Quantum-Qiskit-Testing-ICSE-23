from cProfile import run
from functools import reduce
from qiskit import QuantumRegister, ClassicalRegister
from qiskit import QuantumCircuit, execute, Aer
from pytket.extensions.qiskit import qiskit_to_tk, tk_to_qiskit
from pytket.qasm import circuit_from_qasm
import numpy as np
import re
import cirq
import qiskit

import cProfile, pstats, io
from pstats import SortKey

from lib.multi_platform_interface import execute_qiskit_and_cirq
from lib.multi_platform_interface import run_cirq
from lib.multi_platform_interface import run_qiskit


# Copyright 2019-2022 Cambridge Quantum Computing
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Methods to allow conversion between Cirq and tket data types, including Circuits and
Devices
"""

from typing import List, Dict, FrozenSet, cast, Any
import cmath
from logging import warning
from cirq.devices import LineQubit, GridQubit
import cirq.ops
import cirq_google
from pytket.circuit import Circuit, OpType, Qubit, Bit, Node  # type: ignore
from pytket.routing import Architecture  # type: ignore
from sympy import pi  # type: ignore

# For translating cirq circuits to tket circuits
cirq_common = cirq.ops.common_gates
cirq_pauli = cirq.ops.pauli_gates

from cirq.circuits.qasm_output import QasmUGate

cirq_CH = cirq_common.H.controlled(1)

class MappingObject(object):

    def __init__(self,
                 cirq_op, tket_op,
                 preferred_to_cirq: bool=True, preferred_to_tk: bool=True):
        self.cirq_op = cirq_op
        self.tket_op = tket_op
        # whether this mapping is the preferred one to
        # go from tk to cirq. This is necessary because
        # the same gate could be associated to multiple gates in
        # one direction, thus reversing we need to choose a preferred
        # one since the association is not injective.
        self.preferred_to_cirq = preferred_to_cirq
        self.preferred_to_tk = preferred_to_tk

_cirq2ops_mapping_objects = [
    MappingObject(cirq_common.CNOT, OpType.CX),
    MappingObject(cirq.TOFFOLI, OpType.CCX),
    MappingObject(cirq_common.H, OpType.H),
    MappingObject(cirq_common.MeasurementGate, OpType.Measure),
    MappingObject(cirq_common.XPowGate, OpType.Rx, preferred_to_cirq=False),
    MappingObject(cirq_common.YPowGate, OpType.Ry, preferred_to_cirq=False),
    MappingObject(cirq_common.ZPowGate, OpType.Rz, preferred_to_cirq=False),
    MappingObject(cirq_common.Rx, OpType.Rx, preferred_to_cirq=True),
    MappingObject(cirq_common.Ry, OpType.Ry, preferred_to_cirq=True),
    MappingObject(cirq_common.Rz, OpType.Rz, preferred_to_cirq=True),
    MappingObject(cirq_common.XPowGate(exponent=0.5), OpType.V),
    MappingObject(cirq_common.XPowGate(exponent=-0.5), OpType.Vdg),
    MappingObject(cirq_common.S, OpType.S),
    MappingObject(cirq_common.SWAP, OpType.SWAP),
    MappingObject(cirq_common.T, OpType.T),
    MappingObject(cirq_pauli.X, OpType.X),
    MappingObject(cirq_pauli.Y, OpType.Y),
    MappingObject(cirq_pauli.Z, OpType.Z),
    MappingObject(cirq.ops.I, OpType.noop),
    MappingObject(cirq_common.CZPowGate, OpType.CU1),
    MappingObject(cirq_common.CZ, OpType.CZ),
    MappingObject(cirq_CH, OpType.CH),
    MappingObject(cirq.ops.CSwapGate, OpType.CSWAP),
    MappingObject(cirq_common.ISwapPowGate, OpType.ISWAP),
    MappingObject(cirq_common.ISWAP, OpType.ISWAPMax),
    MappingObject(cirq.ops.FSimGate, OpType.FSim),
    MappingObject(cirq_google.SYC, OpType.Sycamore),
    MappingObject(cirq.ops.parity_gates.ZZPowGate, OpType.ZZPhase),
    MappingObject(cirq.ops.parity_gates.XXPowGate, OpType.XXPhase),
    MappingObject(cirq.ops.parity_gates.YYPowGate, OpType.YYPhase),
    MappingObject(cirq.ops.PhasedXPowGate, OpType.PhasedX),
    MappingObject(cirq.ops.PhasedISwapPowGate, OpType.PhasedISWAP),
    # ADDITION
    MappingObject(QasmUGate, OpType.U3, preferred_to_tk=True),
    MappingObject(QasmUGate, OpType.U2, preferred_to_tk=False),
    MappingObject(QasmUGate, OpType.U1, preferred_to_tk=False)
    # MappingObject(QasmUGate, OpType.Barrier, preferred_to_tk=False)
]


# map cirq common gates to pytket gates
_cirq2ops_mapping: Dict = {
    map_obj.cirq_op : map_obj.tket_op
    for map_obj in _cirq2ops_mapping_objects
    if map_obj.preferred_to_tk
}
# reverse mapping for convenience
_ops2cirq_mapping: Dict = {
    map_obj.tket_op : map_obj.cirq_op
    for map_obj in _cirq2ops_mapping_objects
    if map_obj.preferred_to_cirq
}
# spot special rotation gates
_constant_gates = (
    cirq_common.CNOT,
    cirq_common.H,
    cirq_common.S,
    cirq_common.SWAP,
    cirq_common.T,
    cirq_pauli.X,
    cirq_pauli.Y,
    cirq_pauli.Z,
    cirq_common.CZ,
    cirq_CH,
    cirq_common.ISWAP,
    cirq_google.SYC,
    cirq.ops.I,
)
_rotation_types = (
    cirq_common.XPowGate,
    cirq_common.YPowGate,
    cirq_common.ZPowGate,
    cirq_common.CZPowGate,
    cirq_common.ISwapPowGate,
    cirq.ops.parity_gates.ZZPowGate,
    cirq.ops.parity_gates.XXPowGate,
    cirq.ops.parity_gates.YYPowGate,
)


def my_cirq_to_tk(circuit: cirq.circuits.Circuit) -> Circuit:
    """Converts a Cirq :py:class:`Circuit` to a tket :py:class:`Circuit` object.

    :param circuit: The input Cirq :py:class:`Circuit`

    :raises NotImplementedError: If the input contains a Cirq :py:class:`Circuit`
        operation which is not yet supported by pytket

    :return: The tket :py:class:`Circuit` corresponding to the input circuit
    """
    tkcirc = Circuit()
    qmap = {}
    for qb in circuit.all_qubits():
        if isinstance(qb, LineQubit):
            uid = Qubit("q", qb.x)
        elif isinstance(qb, GridQubit):
            uid = Qubit("g", qb.row, qb.col)
        elif isinstance(qb, cirq.ops.NamedQubit):
            uid = Qubit(qb.name)
        else:
            raise NotImplementedError("Cannot convert qubits of type " + str(type(qb)))
        tkcirc.add_qubit(uid)
        qmap.update({qb: uid})
    for moment in circuit:
        for op in moment.operations:
            if isinstance(op, cirq.ops.GlobalPhaseOperation):
                tkcirc.add_phase(cmath.phase(op.coefficient) / pi)
                continue
            gate = op.gate
            gatetype = type(gate)
            qb_lst = [qmap[q] for q in op.qubits]

            if isinstance(gate, cirq_common.HPowGate) and gate.exponent == 1:
                gate = cirq_common.H
            elif (
                gatetype == cirq_common.CNotPowGate
                and cast(cirq_common.CNotPowGate, gate).exponent == 1
            ):
                gate = cirq_common.CNOT
            elif (
                gatetype == cirq_pauli._PauliX
                and cast(cirq_pauli._PauliX, gate).exponent == 1
            ):
                gate = cirq_pauli.X
            elif (
                gatetype == cirq_pauli._PauliY
                and cast(cirq_pauli._PauliY, gate).exponent == 1
            ):
                gate = cirq_pauli.Y
            elif (
                gatetype == cirq_pauli._PauliZ
                and cast(cirq_pauli._PauliZ, gate).exponent == 1
            ):
                gate = cirq_pauli.Z

            apply_in_parallel = False
            if isinstance(gate, cirq.ops.ParallelGate):
                if gate.num_copies != len(qb_lst):
                    raise NotImplementedError(
                        "ParallelGate parameters defined incorrectly."
                    )
                gate = gate.sub_gate
                gatetype = type(gate)
                apply_in_parallel = True

            if gate in _constant_gates:
                try:
                    optype = _cirq2ops_mapping[gate]
                except KeyError as error:
                    raise NotImplementedError(
                        "Operation not supported by tket: " + str(op.gate)
                    ) from error
                params = []
            elif isinstance(gate, cirq_common.MeasurementGate):
                uid = Bit(gate.key)
                tkcirc.add_bit(uid)
                tkcirc.Measure(*qb_lst, uid)
                continue
            elif isinstance(gate, cirq.ops.PhasedXPowGate):
                optype = OpType.PhasedX
                pe = gate.phase_exponent
                params = [gate.exponent, pe]
            elif isinstance(gate, cirq.ops.FSimGate):
                optype = OpType.FSim
                params = [gate.theta / pi, gate.phi / pi]
            elif isinstance(gate, cirq.ops.PhasedISwapPowGate):
                optype = OpType.PhasedISWAP
                params = [gate.phase_exponent, gate.exponent]
            ## ADDED
            elif isinstance(gate, cirq.ops.CCNotPowGate):
                optype = OpType.CCX
                params = [gate._exponent]
            ## ADDED
            elif isinstance(gate, QasmUGate):
                # params theta, phi, lmda
                if gate.theta == cmath.pi/2:
                    # U2
                    optype = OpType.U2
                    params = [gate.phi, gate.lmda]
                else:
                    # U3
                    optype = OpType.U3
                    params = [gate.theta, gate.phi, gate.lmda]



            else:
                try:
                    optype = _cirq2ops_mapping[gatetype]
                    params = [cast(Any, gate).exponent]
                except (KeyError, AttributeError) as error:

                    """
                    # CHECK IF IT CAN BE DECOMPOSED
                    object_methods = [
                        method_name
                        for method_name in dir(gate)
                        if callable(getattr(gate, method_name))
                    ]
                    decomposeable_gate = "_decompose_" in object_methods
                    print(gate)
                    print(object_methods)
                    print(gate.__dict__)
                    print(decomposeable_gate)
                    subparts = gate._decompose_(gate._num_qubits)
                    print("subparts:", subparts)
                    new_sub_circuit = cirq.circuits.Circuit()
                    for supart in subparts:
                        new_sub_circuit.append(supart)

                    print(new_sub_circuit)
                    """

                    raise NotImplementedError(
                        "Operation not supported by tket: " + str(op.gate)
                    ) from error
            if apply_in_parallel:
                for qb in qb_lst:
                    tkcirc.add_gate(optype, params, [qb])
            else:
                tkcirc.add_gate(optype, params, qb_lst)
    return tkcirc


def my_tk_to_cirq(tkcirc: Circuit, copy_all_qubits: bool = False) -> cirq.circuits.Circuit:
    """Converts a tket :py:class:`Circuit` object to a Cirq :py:class:`Circuit`.

    :param tkcirc: The input tket :py:class:`Circuit`

    :return: The Cirq :py:class:`Circuit` corresponding to the input circuit
    """
    if copy_all_qubits:
        tkcirc = tkcirc.copy()
        for q in tkcirc.qubits:
            tkcirc.add_gate(OpType.noop, [q])

    qmap = {}
    line_name = None
    grid_name = None
    # Since Cirq can only support registers of up to 2 dimensions, we explicitly
    # check for 3-dimensional registers whose third dimension is trivial.
    # SquareGrid architectures are of this form.
    indices = [qb.index for qb in tkcirc.qubits]
    is_flat_3d = all(idx[2] == 0 for idx in indices if len(idx) == 3)
    for qb in tkcirc.qubits:
        if len(qb.index) == 0:
            qmap.update({qb: cirq.ops.NamedQubit(qb.reg_name)})
        elif len(qb.index) == 1:
            if line_name != None and line_name != qb.reg_name:
                raise NotImplementedError(
                    "Cirq can only support a single linear register"
                )
            line_name = qb.reg_name
            qmap.update({qb: LineQubit(qb.index[0])})
        elif len(qb.index) == 2 or (len(qb.index) == 3 and is_flat_3d):
            if grid_name != None and grid_name != qb.reg_name:
                raise NotImplementedError(
                    "Cirq can only support a single grid register"
                )
            grid_name = qb.reg_name
            qmap.update({qb: GridQubit(qb.index[0], qb.index[1])})
        else:
            raise NotImplementedError(
                "Cirq can only support registers of dimension <=2"
            )
    oplst = []
    for command in tkcirc:
        op = command.op
        optype = op.type
        try:
            gatetype = _ops2cirq_mapping[optype]
        except KeyError as error:
            # ADDITION: SKIP BARRIER SINCE THEY ARE NOT SUPPORTED BY CIRQ
            if optype == OpType.Barrier:
                continue
            raise NotImplementedError(
                "Cannot convert tket Op to Cirq gate: " + op.get_name()
            ) from error
        if optype == OpType.Measure:
            qid = qmap[command.args[0]]
            bit = command.args[1]
            cirqop = cirq.ops.measure(qid, key=bit.__repr__())
        else:
            qids = [qmap[qbit] for qbit in command.args]
            params = op.params
            # DEBUG -> print(optype) print("params:", params)
            if len(params) == 0:
                cirqop = gatetype(*qids)
            elif optype == OpType.PhasedX:
                cirqop = gatetype(phase_exponent=params[1], exponent=params[0])(*qids)
            elif optype == OpType.FSim:
                cirqop = gatetype(
                    theta=float(params[0] * pi), phi=float(params[1] * pi)
                )(*qids)
            elif optype == OpType.PhasedISWAP:
                cirqop = gatetype(phase_exponent=params[0], exponent=params[1])(*qids)
            # ADDITION
            elif optype == OpType.U3:
                cirqop = gatetype(theta=params[0], phi=params[1], lmda=params[2])(*qids)
            # ADDITION
            elif optype == OpType.U2:
                cirqop = gatetype(theta=0.5, phi=params[0], lmda=params[1])(*qids)
            # ADDITION
            elif optype == OpType.U1:
                cirqop = gatetype(theta=0, phi=0, lmda=params[0])(*qids)
            # ADDITION
            elif optype == OpType.Rx or optype == OpType.Ry or optype == OpType.Rz:
                cirqop = gatetype(rads=params[0]*cmath.pi)(*qids)
            else:
                cirqop = gatetype(exponent=params[0])(*qids)
        oplst.append(cirqop)
    try:

        coeff = cmath.exp(float(tkcirc.phase) * cmath.pi * 1j)
        if coeff.real < 1e-8:  # tolerance permitted by cirq for GlobalPhaseOperation
            coeff = coeff.imag * 1j
        if coeff.imag < 1e-8:
            coeff = coeff.real
        if coeff != 1.0:
            oplst.append(cirq.ops.GlobalPhaseOperation(coeff))
    except ValueError:
        warning(
            "Global phase is dependent on a symbolic parameter, so cannot adjust for "
            "phase"
        )
    return cirq.circuits.Circuit(*oplst)


# For converting cirq devices to tket devices


def _sort_row_col(qubits: FrozenSet[GridQubit]) -> List[GridQubit]:
    """Sort grid qubits first by row then by column"""

    return sorted(qubits, key=lambda x: (x.row, x.col))


def process_characterisation(xmon: cirq_google.XmonDevice) -> dict:
    """Generates a tket dictionary containing device characteristics for a Cirq
    :py:class:`XmonDevice`.

    :param xmon: The device to convert

    :return: A dictionary containing device characteristics
    """
    qb_map = {q: Node("q", q.row, q.col) for q in xmon.qubits}

    indexed_qubits = _sort_row_col(xmon.qubits)
    coupling_map = []
    for qb in indexed_qubits:
        neighbours = xmon.neighbors_of(qb)
        for x in neighbours:
            coupling_map.append((qb_map[qb], qb_map[x]))
    arc = Architecture(coupling_map)

    characterisation = dict()
    characterisation["Architecture"] = arc

    return characterisation


def convert_to_qiskit_and_cirq_tket(circ: Circuit, show=False):
    """Convert the Tket circuit in both platforms."""
    qc_qiskit = tk_to_qiskit(circ)
    assert isinstance(qc_qiskit, qiskit.circuit.quantumcircuit.QuantumCircuit)
    qc_cirq = my_tk_to_cirq(circ)
    assert isinstance(qc_cirq, cirq.circuits.circuit.Circuit)
    if show:
        print(type(qc_qiskit))
        print(qc_qiskit)
        print(type(qc_cirq))
        print(qc_cirq)
    return {"qc_qiskit": qc_qiskit, "qc_cirq": qc_cirq}


def extract_function_calls(stats_string: str):
    function_calls = []
    lines = stats_string.splitlines()
    for line in lines:
        m = re.search('site-packages(.+?)$', line)
        if m:
            i_function_call = m.group(1)
            function_calls.append(i_function_call)
    return function_calls


def convert_and_execute_qiskit_and_cirq_via_tket(qasm_path: str, shots: int = 8192) -> Dict[str, Any]:
    """Convert the circuit in both platforms and execute them."""
    circ = circuit_from_qasm(qasm_path)
    pr = cProfile.Profile()
    pr.enable()
    qc_circuits = convert_to_qiskit_and_cirq_tket(circ)
    counts_qiskit_cirq = execute_qiskit_and_cirq(**qc_circuits, shots=shots)
    pr.disable()
    s = io.StringIO()
    sortby = SortKey.CUMULATIVE
    ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
    ps.print_stats()
    ps_output = s.getvalue()
    counts_qiskit_cirq["profile_output"] = ps_output
    counts_qiskit_cirq["profile_function_calls"] = extract_function_calls(ps_output)
    counts_qiskit_cirq["profile_n_function_calls"] = len(counts_qiskit_cirq["profile_function_calls"])
    regex_seconds = re.search('in (\d*\.\d*) seconds', ps_output)
    time = regex_seconds.group(1) if regex_seconds else None
    counts_qiskit_cirq["profile_time"] = time
    return counts_qiskit_cirq


def run_qasm_via_tket(qasm_path: str, platform: str = "qiskit", shots: int = 8192):
    """Run a qasm file with an intermediate translation in tket."""
    circ = circuit_from_qasm(qasm_path)
    if platform == 'qiskit':
        qc_qiskit = tk_to_qiskit(circ)
        counts = run_qiskit(qc_qiskit, shots)
    elif platform == 'cirq':
        qc_cirq = my_tk_to_cirq(circ)
        counts = run_cirq(qc_cirq, shots)
    return counts