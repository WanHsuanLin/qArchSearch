OPENQASM 2.0;
include "qelib1.inc";

qreg q[16];

ch q[0], q[1];
ch q[2], q[3];
ch q[4], q[5];
ch q[6], q[7];

ch q[1], q[2];
ch q[3], q[4];
ch q[5], q[6];

u1(0) q[1];
u1(1) q[3];
u1(2) q[5];
u1(3) q[7];
barrier q;
rx(0) q[0];
rx(1) q[2];
rx(2) q[4];
rx(3) q[6];


ch q[0], q[2];
ch q[4], q[6];

ch q[2], q[4];

u1(4) q[2];
u1(5) q[6];
barrier q;
rx(4) q[0];
rx(5) q[4];

ch q[0], q[4];

u1(6) q[4];
barrier q;
rx(6) q[0];