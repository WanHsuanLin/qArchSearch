from qiskit.transpiler.basepasses import TransformationPass
from cv2 import solve
from qiskit.dagcircuit import DAGCircuit
from qiskit.circuit.library.standard_gates import U1Gate, U2Gate, U3Gate, CXGate
from qiskit.circuit import Measure
from qiskit.circuit.barrier import Barrier
from qiskit.dagcircuit import DAGOpNode
from qiskit.transpiler.exceptions import TranspilerError
from qiskit import QuantumCircuit
from qiskit.converters import circuit_to_dag, dag_to_circuit
from qiskit.providers.models.backendproperties import BackendProperties

import time
import os
import sys
import argparse
import json
dir_path = os.getcwd()
sys.path.append(dir_path)
from qArchSearc.writeCSV import cal_crosstalk
from qArchSearc.device import getNeighboringQubit
from qArchSearc.util import get_list_of_json_files, cal_crosstalk

TWO_QUBIT_GATE_FID = 0.99
CT_TWO_QUBIT_GATE_FID = 0.985
COHERENCE_TIME = 1000

# import warnings
# warnings.filterwarnings('ignore' , 'DeprecationWarning')

# This code is part of Qiskit.
#
# (C) Copyright IBM 2017, 2019.
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE.txt file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.

"""
Crosstalk mitigation through adaptive instruction scheduling.
The scheduling algorithm is described in:
Prakash Murali, David C. McKay, Margaret Martonosi, Ali Javadi Abhari,
Software Mitigation of Crosstalk on Noisy Intermediate-Scale Quantum Computers,
in International Conference on Architectural Support for Programming Languages
and Operating Systems (ASPLOS), 2020.
Please cite the paper if you use this pass.
The method handles crosstalk noise on two-qubit gates. This includes crosstalk
with simultaneous two-qubit and one-qubit gates. The method ignores
crosstalk between pairs of single qubit gates.
The method assumes that all qubits get measured simultaneously whether or not
they need a measurement. This assumption is based on current device properties
and may need to be revised for future device generations.
"""
import math
import operator
from itertools import chain, combinations

try:
    from z3 import Int, Real, Bool, Sum, Implies, And, Or, Not, If, Optimize, sat, Solver

    HAS_Z3 = True
except ImportError:
    HAS_Z3 = False
from qiskit.transpiler.basepasses import TransformationPass
from qiskit.dagcircuit import DAGCircuit
from qiskit.circuit.library.standard_gates import U1Gate, U2Gate, U3Gate, CXGate, HGate
from qiskit.circuit import Measure
from qiskit.circuit.barrier import Barrier
from qiskit.dagcircuit import DAGOpNode
from qiskit.transpiler.exceptions import TranspilerError

NUM_PREC = 10
# TWOQ_XTALK_THRESH = 3
TWOQ_XTALK_THRESH = 1
ONEQ_XTALK_THRESH = 1
timeout = 60*20

class CrosstalkAdaptiveSchedule(TransformationPass):
    """Crosstalk mitigation through adaptive instruction scheduling."""

    def __init__(self, crosstalk_prop, M, max_depth = 1, min_depth = 0, max_ct = 0, g2 = 0, measured_qubits=None):
        """CrosstalkAdaptiveSchedule initializer.

        Args:
            backend_prop (BackendProperties): backend properties object
            crosstalk_prop (dict): crosstalk properties object
                crosstalk_prop[g1][g2] specifies the conditional error rate of
                g1 when g1 and g2 are executed simultaneously.
                g1 should be a two-qubit tuple of the form (x,y) where x and y are physical
                qubit ids. g2 can be either two-qubit tuple (x,y) or single-qubit tuple (x).
                We currently ignore crosstalk between pairs of single-qubit gates.
                Gate pairs which are not specified are assumed to be crosstalk free.

                Example::

                    crosstalk_prop = {(0, 1) : {(2, 3) : 0.2, (2) : 0.15},
                                                (4, 5) : {(2, 3) : 0.1},
                                                (2, 3) : {(0, 1) : 0.05, (4, 5): 0.05}}

                The keys of the crosstalk_prop are tuples for ordered tuples for CX gates
                e.g., (0, 1) corresponding to CX 0, 1 in the hardware.
                Each key has an associated value dict which specifies the conditional error rates
                with nearby gates e.g., ``(0, 1) : {(2, 3) : 0.2, (2) : 0.15}`` means that
                CNOT 0, 1 has an error rate of 0.2 when it is executed in parallel with CNOT 2,3
                and an error rate of 0.15 when it is executed in parallel with a single qubit
                gate on qubit 2.
            weight_factor (float): weight of gate error/crosstalk terms in the objective
                :math:`weight_factor*fidelities + (1-weight_factor)*decoherence errors`.
                Weight can be varied from 0 to 1, with 0 meaning that only decoherence
                errors are optimized and 1 meaning that only crosstalk errors are optimized.
                weight_factor should be tuned per application to get the best results.
            measured_qubits (list): a list of qubits that will be measured in a particular circuit.
                This arg need not be specified for circuits which already include measure gates.
                The arg is useful when a subsequent module such as state_tomography_circuits
                inserts the measure gates. If CrosstalkAdaptiveSchedule is made aware of those
                measurements, it is included in the optimization.
        Raises:
            ImportError: if unable to import z3 solver

        """
        super().__init__()
        self.crosstalk_prop = crosstalk_prop
        self.weight_factor = None
        if measured_qubits is None:
            self.input_measured_qubits = []
        else:
            self.input_measured_qubits = measured_qubits
        self.bp_u1_err = {}
        self.bp_u1_dur = {}
        self.bp_u2_err = {}
        self.bp_u2_dur = {}
        self.bp_u3_err = {}
        self.bp_u3_dur = {}
        self.bp_cx_err = {}
        self.bp_cx_dur = {}
        self.bp_t1_time = {}
        self.bp_t2_time = {}
        self.gate_id = {}
        self.gate_start_time = {}
        self.gate_duration = {}
        self.gate_fidelity = {}
        self.overlap_amounts = {}
        self.overlap_indicator = {}
        self.qubit_lifetime = {}
        self.dag_overlap_set = {}
        self.xtalk_overlap_set = {}
        self.opt = Optimize()
        self.measured_qubits = []
        self.measure_start = None
        self.last_gate_on_qubit = None
        self.first_gate_on_qubit = None
        self.fidelity_terms = []
        self.coherence_terms = []
        self.model = None
        self.dag = None
        self.parse_backend_properties()
        self.qubit_indices = None
        self.max_life_time = None
        self.max_detph = max_depth
        self.min_detph = min_depth
        self.M = M
        self.g2 = g2
        self.max_ct_num = max_ct
        self.count_ct_num = None

    def powerset(self, iterable):
        """
        Finds the set of all subsets of the given iterable
        This function is used to generate constraints for the Z3 optimization
        """
        l_s = list(iterable)
        return chain.from_iterable(combinations(l_s, r) for r in range(len(l_s) + 1))


    def parse_backend_properties(self):
        """
        This function assumes that gate durations and coherence times
        are in seconds in backend.properties()
        This function converts gate durations and coherence times to
        nanoseconds.
        """
        dur = 0.99999
        for qid in range(16):
            self.bp_t1_time[qid] = 1000
            self.bp_t2_time[qid] = 1000
            self.bp_u1_dur[qid] = dur
            u1_err = 0.001
            self.bp_u1_err = round(u1_err, NUM_PREC)
            self.bp_u2_dur[qid] = dur
            u2_err = 0.001
            self.bp_u2_err = round(u2_err, NUM_PREC)
            self.bp_u3_dur[qid] = dur
            u3_err = 0.001
            self.bp_u3_err = round(u3_err, NUM_PREC)
        for edge in self.crosstalk_prop:
            q_0 = edge[0]
            q_1 = edge[1]
            cx_tup = (min(q_0, q_1), max(q_0, q_1))
            self.bp_cx_dur[cx_tup] = dur
            cx_err = 0.01
            self.bp_cx_err[cx_tup] = round(cx_err, NUM_PREC)


    def cx_tuple(self, gate):
        """
        Representation for two-qubit gate
        Note: current implementation assumes that the CX error rates and
        crosstalk behavior are independent of gate direction
        """
        physical_q_0 = self.qubit_indices[gate.qargs[0]]
        physical_q_1 = self.qubit_indices[gate.qargs[1]]
        r_0 = min(physical_q_0, physical_q_1)
        r_1 = max(physical_q_0, physical_q_1)
        return (r_0, r_1)


    def singleq_tuple(self, gate):
        """
        Representation for single-qubit gate
        """
        physical_q_0 = self.qubit_indices[gate.qargs[0]]
        tup = (physical_q_0,)
        return tup


    def gate_tuple(self, gate):
        """
        Representation for gate
        """
        if len(gate.qargs) == 2:
            return self.cx_tuple(gate)
        else:
            return self.singleq_tuple(gate)


    def assign_gate_id(self, dag):
        """
        ID for each gate
        """
        idx = 0
        for gate in dag.gate_nodes():
            self.gate_id[gate] = idx
            idx += 1


    def extract_dag_overlap_sets(self, dag):
        """
        Gate A, B are overlapping if
        A is neither a descendant nor an ancestor of B.
        Currenty overlaps (A,B) are considered when A is a 2q gate and
        B is either 2q or 1q gate.
        """
        for gate in dag.two_qubit_ops():
            overlap_set = []
            descendants = dag.descendants(gate)
            ancestors = dag.ancestors(gate)
            for tmp_gate in dag.gate_nodes():
                if tmp_gate == gate:
                    continue
                if tmp_gate in descendants:
                    continue
                if tmp_gate in ancestors:
                    continue
                overlap_set.append(tmp_gate)
            self.dag_overlap_set[gate] = overlap_set


    def is_significant_xtalk(self, gate1, gate2):
        """
        Given two conditional gate error rates
        check if there is high crosstalk by comparing with independent error rates.
        """
        gate1_tup = self.gate_tuple(gate1)
        if len(gate2.qargs) == 2:
            gate2_tup = self.gate_tuple(gate2)
            independent_err_g_1 = self.bp_cx_err[gate1_tup]
            independent_err_g_2 = self.bp_cx_err[gate2_tup]
            rg_1 = self.crosstalk_prop[gate1_tup][gate2_tup] / independent_err_g_1
            rg_2 = self.crosstalk_prop[gate2_tup][gate1_tup] / independent_err_g_2
            if rg_1 > TWOQ_XTALK_THRESH or rg_2 > TWOQ_XTALK_THRESH:
                return True
        else:
            gate2_tup = self.gate_tuple(gate2)
            independent_err_g_1 = self.bp_cx_err[gate1_tup]
            rg_1 = self.crosstalk_prop[gate1_tup][gate2_tup] / independent_err_g_1
            # print("check ", self.gate_id[gate1], " and ", self.gate_id[gate2], ", the ratio is ", rg_1)
            if rg_1 > ONEQ_XTALK_THRESH:
                return True
        return False


    def extract_crosstalk_relevant_sets(self):
        """
        Extract the set of program gates which potentially have crosstalk noise
        """
        for gate in self.dag_overlap_set:
            self.xtalk_overlap_set[gate] = []
            tup_g = self.gate_tuple(gate)
            if tup_g not in self.crosstalk_prop:
                continue
            for par_g in self.dag_overlap_set[gate]:
                tup_par_g = self.gate_tuple(par_g)
                # print("check ", self.gate_id[gate], " and ", self.gate_id[par_g])
                if tup_par_g in self.crosstalk_prop[tup_g]:
                    if self.is_significant_xtalk(gate, par_g):
                        if par_g not in self.xtalk_overlap_set[gate]:
                            self.xtalk_overlap_set[gate].append(par_g)


    def create_z3_vars(self):
        """
        Setup the variables required for Z3 optimization
        """
        useReal = True
        for gate in self.dag.gate_nodes():
            t_var_name = "t_" + str(self.gate_id[gate])
            d_var_name = "d_" + str(self.gate_id[gate])
            f_var_name = "f_" + str(self.gate_id[gate])
            if useReal:
                self.gate_start_time[gate] = Real(t_var_name)
                self.gate_duration[gate] = Real(d_var_name)
            else:
                self.gate_start_time[gate] = Int(t_var_name)
                self.gate_duration[gate] = Int(d_var_name)
            self.gate_fidelity[gate] = Real(f_var_name)
        for gate in self.xtalk_overlap_set:
            self.overlap_indicator[gate] = {}
            self.overlap_amounts[gate] = {}
        for g_1 in self.xtalk_overlap_set:
            for g_2 in self.xtalk_overlap_set[g_1]:
                if len(g_2.qargs) == 2 and g_1 in self.overlap_indicator[g_2]:
                    self.overlap_indicator[g_1][g_2] = self.overlap_indicator[g_2][g_1]
                    self.overlap_amounts[g_1][g_2] = self.overlap_amounts[g_2][g_1]
                else:
                    # Indicator variable for overlap of g_1 and g_2
                    # print("add overlap variable for ", self.gate_id[g_1], " and ", self.gate_id[g_2])
                    var_name1 = "olp_ind_" + str(self.gate_id[g_1]) + "_" + str(self.gate_id[g_2])
                    self.overlap_indicator[g_1][g_2] = Bool(var_name1)
                    var_name2 = "olp_amnt_" + str(self.gate_id[g_1]) + "_" + str(self.gate_id[g_2])
                    self.overlap_amounts[g_1][g_2] = Real(var_name2)
        active_qubits_list = []
        for gate in self.dag.gate_nodes():
            for q in gate.qargs:
                active_qubits_list.append(self.qubit_indices[q])
        for active_qubit in list(set(active_qubits_list)):
            q_var_name = "l_" + str(active_qubit)
            if useReal:
                self.qubit_lifetime[active_qubit] = Real(q_var_name)
            else:
                self.qubit_lifetime[active_qubit] = Int(q_var_name)

        meas_q = []
        for node in self.dag.op_nodes():
            if isinstance(node.op, Measure):
                meas_q.append(self.qubit_indices[node.qargs[0]])

        self.measured_qubits = list(set(self.input_measured_qubits).union(set(meas_q)))
        if useReal:
            self.measure_start = Real("meas_start")
        else:
            self.measure_start = Int("meas_start")

        # add max life time
        if useReal:
            self.max_life_time = Real("max_life_time")
        else:
            self.max_life_time = Int("max_life_time")

        self.count_ct_num = Int("ct_num")


    def basic_bounds(self):
        """
        Basic variable bounds for optimization
        """
        for gate in self.gate_start_time:
            self.opt.add(self.gate_start_time[gate] >= 0)
        for gate in self.gate_duration:
            q_0 = self.qubit_indices[gate.qargs[0]]
            if isinstance(gate.op, U1Gate) or isinstance(gate.op, HGate):
                dur = self.bp_u1_dur[q_0]
            elif isinstance(gate.op, U2Gate):
                dur = self.bp_u2_dur[q_0]
            elif isinstance(gate.op, U3Gate):
                dur = self.bp_u3_dur[q_0]
            elif isinstance(gate.op, CXGate):
                dur = self.bp_cx_dur[self.cx_tuple(gate)]
            self.opt.add(self.gate_duration[gate] == dur)

    def scheduling_constraints(self):
        """
        DAG scheduling constraints optimization
        Sets overlap indicator variables
        """
        for gate in self.gate_start_time:
            for dep_gate in self.dag.successors(gate):
                if not isinstance(dep_gate, DAGOpNode):
                    continue
                if isinstance(dep_gate.op, Measure):
                    continue
                if isinstance(dep_gate.op, Barrier):
                    continue
                fin_g = self.gate_start_time[gate] + self.gate_duration[gate]
                self.opt.add(self.gate_start_time[dep_gate] > fin_g)
        for g_1 in self.xtalk_overlap_set:
            for g_2 in self.xtalk_overlap_set[g_1]:
                if len(g_2.qargs) == 2 and self.gate_id[g_1] > self.gate_id[g_2]:
                    # Symmetry breaking: create only overlap variable for a pair
                    # of gates
                    continue
                s_1 = self.gate_start_time[g_1]
                f_1 = s_1 + self.gate_duration[g_1]
                s_2 = self.gate_start_time[g_2]
                f_2 = s_2 + self.gate_duration[g_2]
                # This constraint enforces full or zero overlap between two gates
                before = f_1 < s_2
                after = f_2 < s_1
                overlap1 = And(s_2 <= s_1, f_1 <= f_2)
                overlap2 = And(s_1 <= s_2, f_2 <= f_1)
                self.opt.add(Or(before, after, overlap1, overlap2))
                intervals_overlap = And(s_2 <= f_1, s_1 <= f_2)
                self.opt.add(self.overlap_indicator[g_1][g_2] == intervals_overlap)


    def fidelity_constraints(self):
        """
        Set gate fidelity based on gate overlap conditions
        """
        for gate in self.gate_start_time:
            q_0 = self.qubit_indices[gate.qargs[0]]
            no_xtalk = False
            if gate not in self.xtalk_overlap_set:
                no_xtalk = True
            elif not self.xtalk_overlap_set[gate]:
                no_xtalk = True
            if no_xtalk:
                if isinstance(gate.op, U1Gate) or isinstance(gate.op, HGate):
                    fid = math.log(1.0)
                elif isinstance(gate.op, U2Gate):
                    fid = math.log(1.0 - self.bp_u2_err[q_0])
                elif isinstance(gate.op, U3Gate):
                    fid = math.log(1.0 - self.bp_u3_err[q_0])
                elif isinstance(gate.op, CXGate):
                    fid = math.log(1.0 - self.bp_cx_err[self.cx_tuple(gate)])
                self.opt.add(self.gate_fidelity[gate] == round(fid, NUM_PREC))
            else:
                # comb = list(self.powerset(self.xtalk_overlap_set[gate]))
                # xtalk_set = set(self.xtalk_overlap_set[gate])
                # for item in comb:
                #     on_set = item
                #     off_set = [i for i in xtalk_set if i not in on_set]
                #     clauses = []
                #     for tmpg in on_set:
                #         clauses.append(self.overlap_indicator[gate][tmpg])
                #     for tmpg in off_set:
                #         clauses.append(Not(self.overlap_indicator[gate][tmpg]))
                #     err = 0
                #     if not on_set:
                #         err = self.bp_cx_err[self.cx_tuple(gate)]
                #     elif len(on_set) == 1:
                #         on_gate = on_set[0]
                #         err = self.crosstalk_prop[self.gate_tuple(gate)][self.gate_tuple(on_gate)]
                #     else:
                #         err_list = []
                #         for on_gate in on_set:
                #             tmp_prop = self.crosstalk_prop[self.gate_tuple(gate)]
                #             err_list.append(tmp_prop[self.gate_tuple(on_gate)])
                #         err = max(err_list)
                #     if err == 1.0:
                #         err = 0.999999
                #     val = round(math.log(1.0 - err), NUM_PREC)
                #     self.opt.add(Implies(And(*clauses), self.gate_fidelity[gate] == val))
                clauses = []
                for item in self.xtalk_overlap_set[gate]:
                    clauses.append(self.overlap_indicator[gate][item])

                err = self.crosstalk_prop[self.gate_tuple(gate)][self.gate_tuple(self.xtalk_overlap_set[gate][-1])]
                if err == 1.0:
                    err = 0.999999
                val = round(math.log(1-err), NUM_PREC)
                self.opt.add(Implies(Or(*clauses), self.gate_fidelity[gate] == val))

                err = self.bp_cx_err[self.cx_tuple(gate)]
                if err == 1.0:
                    err = 0.999999
                val = round(math.log(1-err), NUM_PREC)
                self.opt.add(Implies(Not(Or(*clauses)), self.gate_fidelity[gate] == val))


    def coherence_constraints(self):
        """
        Set decoherence errors based on qubit lifetimes
        """
        self.last_gate_on_qubit = {}
        for gate in self.dag.topological_op_nodes():
            if isinstance(gate.op, Measure):
                continue
            if isinstance(gate.op, Barrier):
                continue
            if len(gate.qargs) == 1:
                q_0 = self.qubit_indices[gate.qargs[0]]
                self.last_gate_on_qubit[q_0] = gate
            else:
                q_0 = self.qubit_indices[gate.qargs[0]]
                q_1 = self.qubit_indices[gate.qargs[1]]
                self.last_gate_on_qubit[q_0] = gate
                self.last_gate_on_qubit[q_1] = gate

        self.first_gate_on_qubit = {}
        for gate in self.dag.topological_op_nodes():
            if len(gate.qargs) == 1:
                q_0 = self.qubit_indices[gate.qargs[0]]
                if q_0 not in self.first_gate_on_qubit:
                    self.first_gate_on_qubit[q_0] = gate
            else:
                q_0 = self.qubit_indices[gate.qargs[0]]
                q_1 = self.qubit_indices[gate.qargs[1]]
                if q_0 not in self.first_gate_on_qubit:
                    self.first_gate_on_qubit[q_0] = gate
                if q_1 not in self.first_gate_on_qubit:
                    self.first_gate_on_qubit[q_1] = gate

        for q in self.last_gate_on_qubit:
            g_last = self.last_gate_on_qubit[q]
            g_first = self.first_gate_on_qubit[q]
            finish_time = self.gate_start_time[g_last] + self.gate_duration[g_last]
            # start_time = self.gate_start_time[g_first]
            start_time = 0
            if q in self.measured_qubits:
                self.opt.add(self.measure_start >= finish_time)
                self.opt.add(self.qubit_lifetime[q] == self.measure_start - start_time)
            else:
                # All qubits get measured simultaneously whether or not they need a measurement
                self.opt.add(self.measure_start >= finish_time)
                self.opt.add(self.qubit_lifetime[q] == finish_time - start_time)

    def setMaxLifetime(self):
        for q in self.qubit_lifetime:
            self.opt.add(self.qubit_lifetime[q] < self.max_life_time)

    def setMaxCtNum(self):
        all_terms = []
        for g_1 in self.xtalk_overlap_set:
            all_terms.append(If(Or([self.overlap_indicator[g_1][g_2] for g_2 in self.xtalk_overlap_set[g_1]]), 1, 0))
        self.opt.add(Sum(all_terms) == self.count_ct_num)

    def r2f(self, val):
        """
        Convert Z3 Real to Python float
        """
        return float(val.as_decimal(16).rstrip("?"))
        # return val.as_long()


    def extract_solution(self):
        """
        Extract gate start and finish times from Z3 solution
        """
        # self.model = self.opt.model()
        result = {}
        maxDepth = 0
        for tmpg in self.gate_start_time:
            start = int(self.r2f(self.model[self.gate_start_time[tmpg]]))
            dur = int(self.r2f(self.model[self.gate_duration[tmpg]]))
            result[tmpg] = (start, start + dur)
            maxDepth = max(maxDepth, start + dur)
            # if len(tmpg.qargs) == 2:
            #     print(self.gate_id[tmpg], self.cx_tuple(tmpg), " start at ", start, " end at ", start+dur)
            # else:
            #     print(self.gate_id[tmpg], self.gate_tuple(tmpg), " start at ", start, " end at ", start+dur)
            # maxDepth = max(maxDepth, int(start + dur))
        
        crosstalk_gates = set()
        for g_1 in self.xtalk_overlap_set:
            for g_2 in self.xtalk_overlap_set[g_1]:
                # print(self.gate_id[g_1], ", " ,self.gate_id[g_2], " : ", self.model[self.overlap_indicator[g_1][g_2]])
                if self.model[self.overlap_indicator[g_1][g_2]]:
                    # print(self.gate_id[g_1], " and ", self.gate_id[g_2], " are overlaop")
                    crosstalk_gates.add(self.gate_id[g_1])
                    if g_2 in self.xtalk_overlap_set:
                        crosstalk_gates.add(self.gate_id[g_2])
        # print(crosstalk_gates)
        # print(self.model[self.count_ct_num])
        assert(len(crosstalk_gates) == self.model[self.count_ct_num])
        # print(self.model[self.max_life_time])
        # print("qubit life time")
        # for q in self.qubit_lifetime:
        #     print(self.r2f(self.model[self.qubit_lifetime[q]]))
        # print(self.r2f(self.model[self.max_life_time]))
        # print(maxDepth)
        return result, self.model[self.count_ct_num].as_long(), maxDepth

    def cal_fidelity_ct(self, ct_num, depth):
        num_g = len(self.gate_id)
        fid = pow(CT_TWO_QUBIT_GATE_FID, (ct_num)) * pow(TWO_QUBIT_GATE_FID, (self.g2 - ct_num)) * math.exp(-(self.M * depth - self.g2 - num_g )/COHERENCE_TIME)
        return fid
  
    def solve_optimization(self):
        """
        Setup and solve a Z3 optimization for finding the best schedule
        """
        solved = False
        model = None
        self.opt = Solver()
        self.create_z3_vars()
        self.basic_bounds()
        self.scheduling_constraints()
        # self.fidelity_constraints()
        self.coherence_constraints()
        self.setMaxLifetime()
        self.setMaxCtNum()
        # set timeout to be 20 min
        self.opt.set("timeout", timeout)
        # begin pop and push
        best_result = None
        best_crosstalkNum = None
        best_depth = None
        best_fid = self.cal_fidelity_ct(self.max_ct_num, self.min_detph)
        print("     Initial solution: ct num->%i, depth->%i, and best_fid: %.4f" % (self.max_ct_num, self.min_detph, best_fid))
        for d in range(self.min_detph, self.max_detph, 3):
            # minimize crosstalk           
            min_ct = 0
            max_ct = self.max_ct_num - 0.2 * self.M * (d - self.min_detph)
            if d == self.min_detph:
                max_ct -= 1
            # if ct < max_ct is UNSAT then no way to improve
            print("     Try depth %i with max crosstalk num %i" % (d, max_ct))
            satisfiable = self.opt.check(self.count_ct_num <= max_ct, self.max_life_time < d)
            if not satisfiable  == sat:
                print("         => fail for this depth")
                continue
            else:
                print("         Start optimizing crosstalk number for depth %i..." % (d))
                while min_ct < max_ct:
                    cur_ct = (max_ct + min_ct)//2
                    print("             Try crosstalk num %i" % (cur_ct))
                    satisfiable = self.opt.check(self.count_ct_num <= cur_ct, self.max_life_time < d)
                    if satisfiable == sat:
                        model = self.opt.model()
                        self.model = model
                        # Extract the schedule computed by Z3
                        result, crosstalkNum, depth = self.extract_solution()
                        cur_fid = self.cal_fidelity_ct(crosstalkNum, depth)
                        if best_fid < cur_fid:
                            print("             FIND BETTER SOLUTION with cur_fid %.6f" % (cur_fid))
                            best_result = result
                            best_crosstalkNum = crosstalkNum
                            best_depth = depth
                            best_fid = cur_fid
                        max_ct = crosstalkNum
                    else:
                        min_ct = cur_ct + 1
        return best_result, best_crosstalkNum, best_depth


    def check_dag_dependency(self, gate1, gate2):
        """
        gate2 is a DAG dependent of gate1 if it is a descendant of gate1
        """
        return gate2 in self.dag.descendants(gate1)


    def check_xtalk_dependency(self, t_1, t_2):
        """
        Check if two gates have a crosstalk dependency.
        We do not consider crosstalk between pairs of single qubit gates.
        """
        g_1 = t_1[0]
        s_1 = t_1[1]
        f_1 = t_1[2]
        g_2 = t_2[0]
        s_2 = t_2[1]
        f_2 = t_2[2]
        if len(g_1.qargs) == 1 and len(g_2.qargs) == 1:
            return False, ()
        if s_2 <= f_1 and s_1 <= f_2:
            # Z3 says it's ok to overlap these gates,
            # so no xtalk dependency needs to be checked
            return False, ()
        else:
            # Assert because we are iterating in Z3 gate start time order,
            # so if two gates are not overlapping, then the second gate has to
            # start after the first gate finishes
            assert s_2 >= f_1
            # Not overlapping, but we care about this dependency
            if len(g_1.qargs) == 2 and len(g_2.qargs) == 2:
                if g_2 in self.xtalk_overlap_set[g_1]:
                    cx1 = self.cx_tuple(g_1)
                    cx2 = self.cx_tuple(g_2)
                    barrier = tuple(sorted([cx1[0], cx1[1], cx2[0], cx2[1]]))
                    return True, barrier
            elif len(g_1.qargs) == 1 and len(g_2.qargs) == 2:
                if g_1 in self.xtalk_overlap_set[g_2]:
                    singleq = self.gate_tuple(g_1)[0]
                    cx1 = self.cx_tuple(g_2)
                    # print(singleq, cx1)
                    barrier = tuple(sorted([singleq, cx1[0], cx1[1]]))
                    return True, barrier
            elif len(g_1.qargs) == 2 and len(g_2.qargs) == 1:
                if g_2 in self.xtalk_overlap_set[g_1]:
                    singleq = self.gate_tuple(g_2)[0]
                    cx1 = self.cx_tuple(g_1)
                    # print(singleq, cx1)
                    barrier = tuple(sorted([singleq, cx1[0], cx1[1]]))
                    return True, barrier
            # Not overlapping, and we don't care about xtalk between these two gates
            return False, ()


    def filter_candidates(self, candidates, layer, layer_id, triplet):
        """
        For a gate G and layer L,
        L is a candidate layer for G if no gate in L has a DAG dependency with G,
        and if Z3 allows gates in L and G to overlap.
        """
        curr_gate = triplet[0]
        for prev_triplet in layer:
            prev_gate = prev_triplet[0]
            is_dag_dep = self.check_dag_dependency(prev_gate, curr_gate)
            is_xtalk_dep, _ = self.check_xtalk_dependency(prev_triplet, triplet)
            if is_dag_dep or is_xtalk_dep:
                # If there is a DAG dependency, we can't insert in any previous layer
                # If there is Xtalk dependency, we can (in general) insert in previous layers,
                # but since we are iterating in the order of gate start times,
                # we should only insert this gate in subsequent layers
                for i in range(layer_id + 1):
                    if i in candidates:
                        candidates.remove(i)
            return candidates


    def find_layer(self, layers, triplet):
        """
        Find the appropriate layer for a gate
        """
        candidates = list(range(len(layers)))
        for i, layer in enumerate(layers):
            candidates = self.filter_candidates(candidates, layer, i, triplet)
        if not candidates:
            return len(layers)
            # Open a new layer
        else:
            return max(candidates)

            # Latest acceptable layer, right-alignment

    def generate_barriers(self, layers):
        """
        For each gate g, see if a barrier is required to serialize it with
        some previously processed gate
        """
        barriers = []
        for i, layer in enumerate(layers):
            barriers.append(set())
            if i == 0:
                continue
            for t_2 in layer:
                for j in range(i):
                    prev_layer = layers[j]
                    for t_1 in prev_layer:
                        is_dag_dep = self.check_dag_dependency(t_1[0], t_2[0])
                        is_xtalk_dep, curr_barrier = self.check_xtalk_dependency(t_1, t_2)
                        if is_dag_dep:
                            # Don't insert a barrier since there is a DAG dependency
                            continue
                        if is_xtalk_dep:
                            # Insert a barrier for this layer
                            barriers[-1].add(curr_barrier)
        return barriers


    def create_updated_dag(self, layers, barriers):
        """
        Given a set of layers and barriers, construct a new dag
        """
        new_dag = DAGCircuit()
        for qreg in self.dag.qregs.values():
            new_dag.add_qreg(qreg)
        for creg in self.dag.cregs.values():
            new_dag.add_creg(creg)
        canonical_register = new_dag.qregs["q"]
        for i, layer in enumerate(layers):
            curr_barriers = barriers[i]
            for b in curr_barriers:
                current_qregs = []
                for idx in b:
                    current_qregs.append(canonical_register[idx])
                new_dag.apply_operation_back(Barrier(len(b)), current_qregs, [])
            for triplet in layer:
                gate = triplet[0]
                new_dag.apply_operation_back(gate.op, gate.qargs, gate.cargs)

        for node in self.dag.op_nodes():
            if isinstance(node.op, Measure):
                new_dag.apply_operation_back(node.op, node.qargs, node.cargs)

        return new_dag


    def enforce_schedule_on_dag(self, input_gate_times):
        """
        Z3 outputs start times for each gate.
        Some gates need to be serialized to implement the Z3 schedule.
        This function inserts barriers to implement those serializations
        """
        gate_times = []
        for key in input_gate_times:
            gate_times.append((key, input_gate_times[key][0], input_gate_times[key][1]))
        # Sort gates by start time
        sorted_gate_times = sorted(gate_times, key=operator.itemgetter(1))
        layers = []
        # Construct a set of layers. Each layer has a set of gates that
        # are allowed to fire in parallel according to Z3
        for triplet in sorted_gate_times:
            layer_idx = self.find_layer(layers, triplet)
            if layer_idx == len(layers):
                layers.append([triplet])
            else:
                layers[layer_idx].append(triplet)
        # Insert barriers if necessary to enforce the above layers
        barriers = self.generate_barriers(layers)
        new_dag = self.create_updated_dag(layers, barriers)
        return new_dag


    def reset(self):
        """
        Reset variables
        """
        self.gate_id = {}
        self.gate_start_time = {}
        self.gate_duration = {}
        self.gate_fidelity = {}
        self.overlap_amounts = {}
        self.overlap_indicator = {}
        self.qubit_lifetime = {}
        self.dag_overlap_set = {}
        self.xtalk_overlap_set = {}
        self.measured_qubits = []
        self.measure_start = None
        self.last_gate_on_qubit = None
        self.first_gate_on_qubit = None
        self.fidelity_terms = []
        self.coherence_terms = []
        self.model = None

    def run(self, dag):
        """
        Main scheduling function
        """
        if not HAS_Z3:
            raise TranspilerError(
                "z3-solver is required to use CrosstalkAdaptiveSchedule. "
                'To install, run "pip install z3-solver".'
            )

        self.dag = dag

        # process input program
        self.qubit_indices = {bit: idx for idx, bit in enumerate(dag.qubits)}
        self.assign_gate_id(self.dag)
        self.extract_dag_overlap_sets(self.dag)
        self.extract_crosstalk_relevant_sets()

        # setup and solve a Z3 optimization
        z3_result, crosstalkNum, depth = self.solve_optimization()
        # print(z3_result)
        # post-process to insert barriers
        if z3_result == None:
            print("     FAIL to find better solution")
            new_dag = None
        else:
            new_dag = self.enforce_schedule_on_dag(z3_result)
        # print("crosstalkNum: ",crosstalkNum)
        # numCrosstalk = self.cal_crosstalk(z3_result)
        self.reset()

        return new_dag, crosstalkNum, depth


# decompse the gates
def decomposeGate(data):
    circuit = QuantumCircuit(16, 0)
    cg = ["SWAP"] * 16
    for gate_pos, gate_type in zip(data["gates"],data["gate_spec"]):
        for pos, gtype in zip(gate_pos, gate_type):
            if gtype == " H":
                circuit.h(pos[0])
            elif gtype == "SWAP" or gtype == " swap":
            # if gtype == "SWAP" or gtype == " swap":
                # add 3 CNOT
                circuit.cx(pos[0],pos[1])
                circuit.cx(pos[0],pos[1])
                circuit.cx(pos[0],pos[1])
            elif gtype == "u4" or gtype == " U4" or gtype == " U4 swap" :
                if cg[pos[0]] == cg[pos[1]]:
                    if cg[pos[0]] == "SWAP" or gtype == " swap":
                        # add full U4
                        circuit.h(pos[0])
                        circuit.h(pos[1])
                    circuit.cx(pos[0], pos[1])
                    circuit.h(pos[0])
                    circuit.h(pos[1])
                    circuit.cx(pos[0], pos[1])
                    circuit.h(pos[1])
                    circuit.cx(pos[0], pos[1])
                    circuit.h(pos[0])
                    circuit.h(pos[1])
                else:
                    if (cg[pos[0]] == "SWAP" or gtype == " swap") and (cg[pos[1]] == "u4" or gtype == " U4"  or gtype == " U4 swap"):
                        circuit.h(pos[0])
                    elif (cg[pos[0]] == "u4" or gtype == " U4"  or gtype == " U4 swap") and (cg[pos[1]] == "SWAP" or gtype == " swap"):
                        circuit.h(pos[1])
                    else:
                        print(gtype)
                        assert (False)
                    circuit.cx(pos[0], pos[1])
                    circuit.h(pos[0])
                    circuit.h(pos[1])
                    circuit.cx(pos[0], pos[1])
                    circuit.h(pos[1])
                    circuit.cx(pos[0], pos[1])
                    circuit.h(pos[0])
                    circuit.h(pos[1])
            else:
                print(gtype)
                assert (False)
            if gtype == "u4" or gtype == " U4" or gtype == " U4 swap":
                cg[pos[0]] = "u4"
                cg[pos[1]] = "u4"
            elif gtype == "SWAP" or gtype == " swap":
                cg[pos[0]] = "SWAP"
                cg[pos[1]] = "SWAP"
    return circuit

# create backend property
def getCtProp(data):
    ct_err = 0.015
    # ct_err = 0.15
    crosstalk_prop = dict()  
    neighboringQubit = getNeighboringQubit(data["extra_edge"])
    flat_gates = [pos for gate_pos in data["gates"] for pos in gate_pos]
    for gate in flat_gates:
        if len(gate) == 2:
            crosstalk_prop[min(gate[0],gate[1]), max(gate[0],gate[1])] = dict()
    for gate in crosstalk_prop:
        for i in range(2):
            for qubit in neighboringQubit[gate[i]]:
                if gate[0] != qubit and gate[1] != qubit:
                    # add single qubit crosstalk
                    crosstalk_prop[gate][(qubit,)] = ct_err
                    # crosstalk_prop[gate][qubit] = ct_err
                    # add two qubit crosstalk
                    for nqubit in neighboringQubit[qubit]:
                        if gate[0] != qubit and gate[0] != nqubit and gate[1] != qubit and gate[1] != nqubit:
                            crosstalk_prop[gate][(min(qubit,nqubit), max(qubit,nqubit))] = ct_err
    return crosstalk_prop

# Run scheduler
def scheduler(data, max_depth, min_depth, max_ct):
    # decompose gate to basic single qubit and two qubit gate
    # print("Enter scheduler...")
    circuit = decomposeGate(data)
    # circuit.draw(scale=0.7, filename="dcp_cir.png", output='mpl')
    # construct the DAGcircuit
    dag_cir = circuit_to_dag(circuit)
    # dag_cir.draw(scale=0.7, filename="dcp_dag.png", style='color')
    # create crosstalk_prop
    crosstalk_prop = getCtProp(data)
    # print(crosstalk_prop)
    # for item in crosstalk_prop:
    #     print(item, " : ", crosstalk_prop[item])
    scheduler = CrosstalkAdaptiveSchedule(crosstalk_prop = crosstalk_prop, M = data["M"], max_depth = max_depth, min_depth = min_depth, max_ct = max_ct, g2 = data["g2"] )
    new_dag_cir, crosstalkNum, D = scheduler.run(dag_cir)
    if new_dag_cir == None:
        return
    else:
        data["D"] = D - 1
        data["crosstalk"] = crosstalkNum
    # print("resulted depth is ", D, ". num of barrier is ", count_opt["barrier"])
    # new_circuit = dag_to_circuit(new_dag_cir)
    # new_dag_cir.draw(scale=0.7, filename="sch_dag.png", style='color')
    # new_circuit.draw(scale=0.7, filename="sch_cir.png", output='mpl')
    # print("total crosstalk number is ", crosstalkNum)


def decideWeight(data):
    M = data["M"]
    weight = 1/(M*math.log(math.e) +1)
    return weight

def calculate_fidelity_bound(data):
    max_fid = data['g2'] * math.log(0.99) - math.log(math.e) * data['D'] * data["M"] / 1000
    crosstalk = cal_crosstalk(data, "qcnn")
    min_fid = (data['g2'] - crosstalk) * math.log(0.99) + crosstalk * math.log(0.985) - math.log(math.e) * data['D'] * data["M"] / 1000
    return max_fid, min_fid

def calculate_max_depth(M, ct, D):
    max_depth = int(ct/ (0.2 * M)) + D
    return max_depth

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    # Adding optional argument
    parser.add_argument("folder", metavar='folder', type=str,
        help="Result Folder: each benchmark result")
    parser.add_argument("new_folder", metavar='new_folder', type=str,
        help="Result Folder: each benchmark result")
    # Read arguments from command line
    args = parser.parse_args()
    list_of_files = get_list_of_json_files(args.folder)
    print("Time limit for z3: %i s" % (timeout))
    for file in list_of_files:
        with open(file) as f:
            print("Start solve device %i" % data["device"])
            data = json.load(f)
            start_time = time.time()
            max_ct = cal_crosstalk(data, "qcnn") 
            max_depth = calculate_max_depth(data["M"], max_ct, data["D"])
            # print("max_depth is ", max_depth)
            scheduler(data, max_depth, data["D"], max_ct)
            print("Execution time: ", time.time() - start_time)
            print("================================================================")
        new_file_name = args.new_folder + "/device" + str(data["device"]) + ".json"
        # with open(file, 'w+') as f:
        with open(new_file_name, 'w+') as f:
            json.dump(data, f)
        print("finish ", new_file_name)
    
