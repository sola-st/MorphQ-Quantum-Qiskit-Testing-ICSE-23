OPENQASM 2.0;
include "qelib1.inc";
qreg q[16];
creg c[16];
cx q[15], q[10];
ry(0.9801424781769557) q[2];
cx q[13], q[9];
ry(6.094123332392967) q[0];
rz(1.1424399624340646) q[3];
cx q[4], q[8];
rx(3.844385118274953) q[4];
cx q[4], q[6];
rx(1.2545873742863833) q[12];
rx(0.29185655071471744) q[9];
ry(0.4087312132537349) q[2];
U(0,5.0793103400482895,0) q[15];
cx q[1], q[11];
rx(3.1112882860657196) q[1];
cx q[14], q[3];
ry(3.267683749398383) q[4];
barrier q;
measure q -> c;