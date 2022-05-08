OPENQASM 2.0;
include "qelib1.inc";

qreg q[12];

ch q[0], q[1];
ch q[2], q[3];
ch q[4], q[5];
ch q[6], q[7];
ch q[8], q[9];
ch q[10], q[11];

ch q[1], q[2];
ch q[3], q[4];
ch q[5], q[6];
ch q[7], q[8];
ch q[9], q[10];

u1(0) q[1];
u1(1) q[3];
u1(2) q[5];
u1(3) q[7];
u1(4) q[9];
u1(5) q[11];
barrier q;
rx(0) q[0];
rx(1) q[2];
rx(2) q[4];
rx(3) q[6];
rx(4) q[8];
rx(5) q[10];

ch q[0], q[2];
ch q[4], q[6];
ch q[8], q[10];

ch q[2], q[4];
ch q[6], q[8];

u1(6) q[2];
u1(7) q[6];
u1(8) q[10];
barrier q;
rx(6) q[0];
rx(7) q[4];
rx(8) q[8];

ch q[0], q[4];

ch q[4], q[8];

u1(9) q[4];
barrier q;
rx(9) q[0];

ch q[0], q[8];

u1(10) q[8];
barrier q;
rx(10) q[0];