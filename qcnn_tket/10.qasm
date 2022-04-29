OPENQASM 2.0;
include "qelib1.inc";

qreg q[10];

CX q[0], q[1];
CX q[2], q[3];
CX q[4], q[5];
CX q[6], q[7];
CX q[8], q[9];

CX q[1], q[2];
CX q[3], q[4];
CX q[5], q[6];
CX q[7], q[8];

CX q[0], q[2];
CX q[4], q[6];

CX q[2], q[4];
CX q[6], q[8];

CX q[0], q[4];

CX q[4], q[8];

CX q[0], q[8];