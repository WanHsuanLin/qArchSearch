OPENQASM 2.0;
include "qelib1.inc";

qreg q[16];

opaque u4 q0, q1;

u4 q[0], q[1];
u4 q[2], q[3];
u4 q[4], q[5];
u4 q[6], q[7];
u4 q[8], q[9];

u4 q[1], q[2];
u4 q[3], q[4];
u4 q[5], q[6];
u4 q[7], q[8];

u4 q[0], q[2];
u4 q[4], q[6];

u4 q[2], q[4];
u4 q[6], q[8];

u4 q[0], q[4];

u4 q[4], q[8];

u4 q[0], q[8];