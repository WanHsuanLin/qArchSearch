OPENQASM 2.0;
include "qelib1.inc";

qreg q[16];

opaque u4 q0, q1;
opaque v0 q0;
opaque v1 q0;
opaque v2 q0;
opaque v3 q0;
opaque v4 q0;
opaque v5 q0;
opaque v6 q0;
opaque m0 q0;
opaque m1 q0;
opaque m2 q0;
opaque m3 q0;
opaque m4 q0;
opaque m5 q0;
opaque m6 q0;

u4 q[0], q[1];
u4 q[2], q[3];
u4 q[4], q[5];
u4 q[6], q[7];

u4 q[1], q[2];
u4 q[3], q[4];
u4 q[5], q[6];

m0 q[1];
m1 q[3];
m2 q[5];
m3 q[7];
barrier q;
v0 q[0];
v1 q[2];
v2 q[4];
v3 q[6];


u4 q[0], q[2];
u4 q[4], q[6];

u4 q[2], q[4];

m4 q[2];
m5 q[6];
barrier q;
v4 q[0];
v5 q[4];

u4 q[0], q[4];

m6 q[4];
barrier q;
v6 q[0];