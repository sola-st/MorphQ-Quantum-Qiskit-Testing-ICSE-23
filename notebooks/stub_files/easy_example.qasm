OPENQASM 2.0;
include "qelib1.inc";
qreg q[4];
creg c[4];
h q[0];
cx q[0], q[1];
ry(1.11) q[2];
rz(2.22) q[2];
cx q[2], q[3];
h q[3];
h q[1];
barrier q;
measure q -> c;