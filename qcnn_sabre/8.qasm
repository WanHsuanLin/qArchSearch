OPENQASM 2.0;
include "qelib1.inc";

qreg q[16];
creg c0[1];
creg c1[1];
creg c2[1];
creg c3[1];

opaque u4 q0, q1;
opaque v1 q0;
opaque v3 q0;
opaque v5 q0;
opaque v7 q0;

u4 q[0], q[1];
u4 q[2], q[3];
u4 q[4], q[5];
u4 q[6], q[7];

u4 q[1], q[2];
u4 q[3], q[4];
u4 q[5], q[6];

measure q[1] -> c0;
measure q[3] -> c1;
measure q[5] -> c2;
measure q[7] -> c3;
barrier q;
if(c0==1) v1 q[0];
if(c1==1) v3 q[2];
if(c2==1) v5 q[4];
if(c3==1) v7 q[6];


u4 q[0], q[2];
u4 q[4], q[6];

u4 q[2], q[4];

u4 q[0], q[4];