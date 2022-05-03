import datetime

from z3 import Int, IntVector, Bool, Implies, And, Or, If, sat, unsat, Solver, set_option, Not

from qArchSearch.olsq.input import input_qasm
from qArchSearch.olsq.device import qcDeviceSet
from qArchSearch.olsq.util import cal_crosstalk, cal_fidelity, cal_QCNN_depth_g2_g1, cal_QAOA_depth
from qArchSearch.gate_absorption import run_gate_absorption
import pkgutil
from enum import Enum

TIMEOUT = 90000
MEMORY_MAX_SIZE = 1000 * 70
MAX_TREAD_NUM = 8
VERBOSE = 10

class Mode(Enum):
    transition = 1
    normal = 2
    mix = 3

def collision_extracting(list_gate_qubits):
    """Extract collision relations between the gates,
    If two gates g_1 and g_2 both acts on a qubit (at different time),
    we say that g_1 and g_2 collide on that qubit, which means that
    (1,2) will be in collision list.

    Args:
        list_gate_qubits: a list of gates in OLSQ IR
    
    Returns:
        list_collision: a list of collisions between the gates
    """

    list_collision = list()
    # We sweep through all the gates.  For each gate, we sweep through all the
    # gates after it, if they both act on some qubit, append them in the list.
    for g in range(len(list_gate_qubits)):
        for gg in range(g + 1, len(list_gate_qubits)):
            
            if list_gate_qubits[g][0] == list_gate_qubits[gg][0]:
                    list_collision.append((g, gg))
                
            if len(list_gate_qubits[gg]) == 2:
                if list_gate_qubits[g][0] == list_gate_qubits[gg][1]:
                    list_collision.append((g, gg))
            
            if len(list_gate_qubits[g]) == 2:
                if list_gate_qubits[g][1] == list_gate_qubits[gg][0]:
                    list_collision.append((g, gg))
                if len(list_gate_qubits[gg]) == 2:
                    if list_gate_qubits[g][1] == list_gate_qubits[gg][1]:
                        list_collision.append((g, gg))
    
    return tuple(list_collision)

def dependency_extracting(list_gate_qubits, count_program_qubit: int):
    """Extract dependency relations between the gates.
    If two gates g_1 and g_2 both acts on a qubit *and there is no gate
    between g_1 and g_2 that act on this qubit*, we then say that
    g2 depends on g1, which means that (1,2) will be in dependency list.

    Args:
        list_gate_qubits: a list of gates in OLSQ IR
        count_program_qubit: the number of logical/program qubit
    
    Returns:
        list_dependency: a list of dependency between the gates
    """

    list_dependency = []
    list_last_gate = [-1 for i in range(count_program_qubit)]
    # list_last_gate records the latest gate that acts on each qubit.
    # When we sweep through all the gates, this list is updated and the
    # dependencies induced by the update is noted.
    for i, qubits in enumerate(list_gate_qubits):
        
        if list_last_gate[qubits[0]] >= 0:
            list_dependency.append((list_last_gate[qubits[0]], i))
        list_last_gate[qubits[0]] = i

        if len(qubits) == 2:
            if list_last_gate[qubits[1]] >= 0:
                list_dependency.append((list_last_gate[qubits[1]], i))
            list_last_gate[qubits[1]] = i

    return tuple(list_dependency)

class qArchEval:
    def __init__(self, mode):
        """Set the objective of OLSQ, and whether it is transition-based

        Args:
            objective_name: can be "depth", "swap", or "fidelity"
            mode: can be "normal" or "transition" (TB-OLSQ in the paper)       
        """

        if mode == "transition":
            self.mode = Mode.transition
        elif mode == "normal":
            self.mode = Mode.normal
        elif mode == "mixed":
            self.mode = Mode.mix
        else:
            raise ValueError("Invalid Choice of Transition-Based or Not")

        # These values should be updated in setdevice(...)
        self.device = None
        self.count_physical_qubit = 0
        self.list_qubit_edge = []
        self.list_extra_qubit_edge = []
        self.list_basic_qubit_edge = []
        self.list_conflict_edge_set = []
        self.swap_duration = 0
        self.dict_gate_duration = dict()
        self.list_gate_duration = []
        self.list_extra_qubit_edge_idx = []
        self.dict_extra_qubit_edge_idx = dict()

        # These values should be updated in setprogram(...)
        self.list_gate_qubits = []
        self.count_program_qubit = 0
        self.list_gate_name = []
        self.list_gate_two = []
        self.list_gate_single = []
        
        # bound_depth is a hyperparameter
        self.bound_depth = 0

        self.inpput_dependency = False
        self.list_gate_dependency = []

        self.benchmark = None

    def setdevice(self, device: qcDeviceSet):
        """Pass in parameters from the given device.  If in TB mode,
           swap_duration is set to 1 without modifying the device.

        Args:
            device: a qcdevice object for OLSQ
        """

        self.device = device
        self.count_physical_qubit = device.count_physical_qubit
        self.list_basic_qubit_edge = device.list_qubit_edge
        self.list_extra_qubit_edge = device.list_extra_qubit_edge
        self.list_qubit_edge = self.list_basic_qubit_edge + self.list_extra_qubit_edge
        self.list_conflict_edge_set = device.conflict_coupling_set
        # print("device basic edge: ", self.list_basic_qubit_edge)
        # print("device extra edge: ", self.list_extra_qubit_edge)
        # print("device all edge: ", self.list_qubit_edge)
        self.swap_duration = device.swap_duration
        if self.mode == Mode.transition:
            self.swap_duration = 1
        # print("show edge idx:")
        for e in self.list_extra_qubit_edge:
            idx = self.list_qubit_edge.index(e)
            self.list_extra_qubit_edge_idx.append(idx)
            self.dict_extra_qubit_edge_idx[e] = idx
            # print(f"edge {e}: {idx}")

    def setprogram(self, benchmark, program, input_mode: str = None, gate_duration: dict = None):
        """Translate input program to OLSQ IR, and set initial depth
        An example of the intermediate representation is shown below.
        It contains three things: 1) the number of qubit in the program,
        2) a list of tuples representing qubit(s) acted on by a gate,
        the tuple has one index if it is a single-qubit gate,
        two indices if it is a two-qubit gate, and 3) a list of
        type/name of each gate, which is not important to OLSQ,
        and only needed when generating output.
        If in TB mode, initial depth=1; in normal mode, we perform ASAP
        scheduling without consideration of SWAP to calculate depth.

        Args:
            program: a qasm string, or a list of the three things in IR.
            input_mode: (optional) can be "IR" if the input has ben
                translated to OLSQ IR; can be "benchmark" to use one of
                the benchmarks.  Default mode assumes qasm input.
            gate_duration: dict: gate name -> duration

        Example:
            For the following circuit
                q_0: ───────────────────■───
                                        │  
                q_1: ───────■───────────┼───
                     ┌───┐┌─┴─┐┌─────┐┌─┴─┐
                q_2: ┤ H ├┤ X ├┤ TDG ├┤ X ├─
                     └───┘└───┘└─────┘└───┘ 
            count_program_qubit = 3
            gates = ((2,), (1,2), (2,), (0,1))
            gate_spec = ("h", "cx", "tdg", "cx")
        """
        
        if input_mode == "IR":
            self.count_program_qubit = program[0]
            self.list_gate_qubits = program[1]
            self.list_gate_name = program[2]
        elif input_mode == "benchmark":
            f = pkgutil.get_data(__name__, "benchmarks/" + program + ".qasm")
            program = input_qasm(f.decode("utf-8"))
            self.count_program_qubit = program[0]
            self.list_gate_qubits = program[1]
            self.list_gate_name = program[2]
        else:
            program = input_qasm(program)
            self.count_program_qubit = program[0]
            self.list_gate_qubits = program[1]
            self.list_gate_name = program[2]


        # create a dict to store the gate duration. Gate name to duration => given as spec
        self.dict_gate_duration = gate_duration
        # create a list to remember the gate duration. gate => duration => construct in when setting program and use for construct constraint.
        if gate_duration != None:
            # self.list_gate_duration
            for gate_name in self.list_gate_name:
                self.list_gate_duration.append(self.dict_gate_duration[gate_name])
        else:
            self.list_gate_duration = [1]*len(self.list_gate_qubits)

        # calculate the initial depth
        # increasing depth will depends on the gate duration
        if self.mode == Mode.transition:
            self.bound_depth = 1
        else:
            push_forward_depth = [0 for i in range(self.count_program_qubit)]
            # for qubits in self.list_gate_qubits:
            for qubits, g_time in zip(self.list_gate_qubits, self.list_gate_duration):
                if len(qubits) == 1:
                    # push_forward_depth[qubits[0]] += 1
                    push_forward_depth[qubits[0]] += g_time
                else:
                    tmp_depth = push_forward_depth[qubits[0]]
                    if tmp_depth < push_forward_depth[qubits[1]]:
                        tmp_depth = push_forward_depth[qubits[1]]
                    push_forward_depth[qubits[1]] = tmp_depth + g_time
                    push_forward_depth[qubits[0]] = tmp_depth + g_time
            self.bound_depth = max(push_forward_depth)
        # print("bound_depth: ", self.bound_depth)

        count_gate = len(self.list_gate_qubits)
        for l in range(count_gate):
            if len(self.list_gate_qubits[l]) == 1:
                self.list_gate_single.append(l)
            else:
                self.list_gate_two.append(l)
        self.benchmark = benchmark

    def setdependency(self, dependency: list):
        """Specify dependency (non-commutation)

        Args:
            dependency: a list of gate index pairs
        
        Example:
            For the following circuit
                q_0: ───────────────────■───
                                        │  
                q_1: ───────■───────────┼───
                     ┌───┐┌─┴─┐┌─────┐┌─┴─┐
                q_2: ┤ H ├┤ X ├┤ TDG ├┤ X ├─
                     └───┘└───┘└─────┘└───┘ 
                gate   0    1     2     3
            dependency = [(0,1), (1,2), (2,3)]

            However, for this QAOA subcircuit (ZZ gates may have phase
            parameters, but we neglect them for simplicity here)
                         ┌──┐ ┌──┐
                q_0: ────┤ZZ├─┤  ├─
                     ┌──┐└┬─┘ │ZZ│  
                q_1: ┤  ├─┼───┤  ├─
                     │ZZ│┌┴─┐ └──┘
                q_2: ┤  ├┤ZZ├──────
                     └──┘└──┘ 
                gate   0   1   2
            dependency = []    # since ZZ gates are commutable
        """
        self.list_gate_dependency = dependency
        self.inpput_dependency = True

    def search(self, folder = None, memory_max_size=MEMORY_MAX_SIZE, verbose = VERBOSE):
        """
        Args:
            output_mode: "IR" or left to default.
            memory_max_alloc_count: set hard upper limit for memory allocations in Z3 (G)
            verbose: verbose stats in Z3
        """
        if not self.inpput_dependency:
            self.list_gate_dependency = collision_extracting(self.list_gate_qubits)
        if self.mode == Mode.transition:
            print("Using transition based mode...")
            _, results = self._search(False, None, folder, memory_max_size, verbose)
        elif self.mode == Mode.normal:
            print("Using normal mode...")
            _, results = self._search(False, None, folder, memory_max_size, verbose)
        elif self.mode == Mode.mix:
            print("Using mixed mode...")
            print("Perform preprocessing to find swap bound...")
            swap_bound, _ = self._search(True, None, None, memory_max_size, verbose)
            print(f"Finish proprocessing. SWAP bound is ({swap_bound[0]},{swap_bound[1]})")
            print("Start normal searching...")
            _, results = self._search(False, swap_bound, folder, memory_max_size, verbose)
        else:
            raise ValueError( ("Wrong type") )
        return results

    def _search(self, preprossess_only, swap_bound, folder = None, memory_max_size=MEMORY_MAX_SIZE, verbose = VERBOSE):
        """Formulate an SMT, pass it to z3 solver, and output results.
        CORE OF OLSQ, EDIT WITH CARE.

        Args:
            preprossess_only: Only used to find the bound for SWAP
        
        Returns:
            a pair of int that specifies the upper and lower bound of SWAP gate counts
            a list of results depending on output_mode
            "IR": 
            | list_scheduled_gate_name: name/type of each gate
            | list_scheduled_gate_qubits: qubit(s) each gate acts on
            | initial_mapping: logical qubit |-> physical qubit 
            | final_mapping: logical qubit |-> physical qubit in the end 
            | objective_value: depth/#swap/fidelity depending on setting
            None:
              a qasm string
              final_mapping
              objective_value
        """

        results = []
        if preprossess_only:
            list_qubit_edge = self.list_basic_qubit_edge
        else:
            list_qubit_edge = self.list_qubit_edge
        # pre-processing
        count_gate = len(self.list_gate_qubits)
        list_gate_duration = self.list_gate_duration
        list_gate_dependency = self.list_gate_dependency

        not_solved = True
        start_time = datetime.datetime.now()
        model = None

        # tight_bound_depth: use for depth constraint

        # bound_depth: generate constraints until t = bound_depth
        if preprossess_only or self.mode == Mode.transition:
            bound_depth = 8 * self.bound_depth
        else:
            bound_depth = 2 * self.bound_depth
        while not_solved:
            print("start adding constraints...")
            # variable setting 
            pi, time, space, sigma, u, count_swap, count_extra_edge = self._construct_variable(bound_depth, len(list_qubit_edge))

            lsqc = Solver()
            # lsqc = SolverFor("QF_BV")
            # set_option("parallel.enable", True)
            # set_option("parallel.threads.max", MAX_TREAD_NUM)
            # if memory_max_size > 0:
            set_option("memory_max_size", MEMORY_MAX_SIZE)
            set_option("timeout", TIMEOUT)
            set_option("verbose", verbose)

            # constraint setting
            self._add_injective_mapping_constraints(bound_depth, pi, lsqc)

            # Consistency between Mapping and Space Coordinates.
            self._add_consistency_gate_constraints(bound_depth, list_qubit_edge, pi, space, time, lsqc)
            
            # Avoiding Collisions and Respecting Dependencies. 
            # Modify dependency constraint
            if preprossess_only or self.mode == Mode.transition:
                for d in list_gate_dependency:
                    lsqc.add(time[d[0]] <= time[d[1]])
            else:
                for d in list_gate_dependency:
                    # lsqc.add(time[d[0]] < time[d[1]])
                    lsqc.add(time[d[0]] + list_gate_duration[d[1]] <= time[d[1]])
                # add initial condition for gates
                for l in range(count_gate):
                    lsqc.add(list_gate_duration[l] - 1 <= time[l])

            # # No swap for t<s
            # # swap gates can not overlap with swap
            self._add_swap_constraints(bound_depth, list_qubit_edge, sigma, lsqc, count_swap)
            # Mapping Not Transformations by SWAP Gates.
            # Mapping Transformations by SWAP Gates.
            self._add_transformation_constraints(bound_depth, list_qubit_edge, lsqc, sigma, pi)

            if not preprossess_only:
                # record the use of the extra edge
                self._add_edge_constraints(bound_depth, count_extra_edge, u, space, sigma, lsqc)
                
            # TODO: iterate each swap num
            for num_e in range(len(self.list_extra_qubit_edge)):
                per_start = datetime.datetime.now()
                
                not_solved, model = self._optimize_circuit(lsqc, preprossess_only, count_extra_edge, num_e, time, count_gate, count_swap, bound_depth, swap_bound)
                if not_solved:
                    bound_depth *= 2
                    break
                if preprossess_only:
                    swap_bound = (self.bound_depth-1 , model[count_swap].as_long())
                    break
                if swap_bound != None:
                    swap_bound = (swap_bound[0],model[count_swap].as_long())
                else:
                    swap_bound = (0,model[count_swap].as_long())
                results.append(self.write_results(model, time, pi, sigma, space, u))
                print(f"Compilation time = {datetime.datetime.now() - per_start}.")
                if folder != None:
                    import json
                    with open(f"./{folder}/extra_edge_{num_e}.json", 'w') as file_object:
                        json.dump(results[num_e], file_object)
                    with open(f"./{folder}_gs/extra_edge_{num_e}.json", 'w') as file_object:
                        device_connection = results[num_e]["extra_edge"] + list(self.list_basic_qubit_edge )
                        run_gate_absorption(self.benchmark, results[num_e], device_connection, self.device.count_physical_qubit)
                        results[num_e]['crosstalk'] = cal_crosstalk(results[num_e], self.benchmark, self.list_qubit_edge, self.device.count_physical_qubit)
                        results[num_e]['fidelity'], results[num_e]['fidelity_ct']  = cal_fidelity(results[num_e])
                        json.dump(results[num_e], file_object)
                lsqc.pop()
                if num_e < 4:
                    continue
                if results[-1]['extra_edge_num'] <= results[-2]['extra_edge_num']:
                    break
                
        print(f"Total compilation time = {datetime.datetime.now() - start_time}.")
        return swap_bound, results

    def _optimize_circuit(self, lsqc, preprossess_only, count_extra_edge, num_e, time, count_gate, count_swap, bound_depth, swap_bound):
        if swap_bound != None:
            print(f"optimizing circuit with swap range ({swap_bound[0]},{swap_bound[1]}) ")
        if swap_bound != None:
            lower_b_swap = swap_bound[0]
            upper_b_swap = swap_bound[-1]
        else:
            upper_b_swap = count_gate
            lower_b_swap = 0
        bound_swap_num = 0
        lsqc.push()
        lsqc.add(count_extra_edge <= num_e)
        find_min_depth = False
        # incremental solving use pop and push
        tight_bound_depth = self.bound_depth
        if preprossess_only:
            tight_bound_depth = 1
        while not find_min_depth:
            print("Trying maximal depth = {}...".format(tight_bound_depth))
            # for depth optimization
            # lsqc.push()
            # for l in range(count_gate):
            #     lsqc.add(tight_bound_depth >= time[l] + 1)
            satisfiable = lsqc.check([tight_bound_depth >= time[l] + 1 for l in range(count_gate)])
            if satisfiable == sat:
                find_min_depth = True
                model = lsqc.model()
                upper_b_swap = min(model[count_swap].as_long(), upper_b_swap)
                if self.mode == Mode.transition:
                    lower_b_swap = tight_bound_depth - 1
                bound_swap_num = (upper_b_swap+lower_b_swap)//2
                # lsqc.add(tight_bound_depth >= time[l] + 1)
            else:
                # lsqc.pop()
                if preprossess_only or self.mode == Mode.transition:
                    tight_bound_depth += 1
                else:
                    tight_bound_depth = int(1.3 * tight_bound_depth)
                print("Show UNSAT core")
                # print unsat core
                core = lsqc.unsat_core()
                print(core)
                if tight_bound_depth > bound_depth:
                    print("FAIL to find depth witnin {}.".format(bound_depth))
                    break
        if not find_min_depth:
            return True, model
        lsqc.add([tight_bound_depth >= time[l] + 1 for l in range(count_gate)])
        # for swap optimization
        find_min_swap = False
        while not find_min_swap:
            print("Bound of Trying min swap = {}...".format(bound_swap_num))
            # lsqc.push()
            # lsqc.add(count_swap <= bound_swap_num)
            # constraint = [tight_bound_depth >= time[l] + 1 for l in range(count_gate)]
            # constraint.append(count_swap <= bound_swap_num)
            satisfiable = lsqc.check(count_swap <= bound_swap_num)
            if satisfiable == sat:
                model = lsqc.model()
                cur_swap = model[count_swap].as_long()
                if cur_swap > lower_b_swap:
                    upper_b_swap = cur_swap
                    bound_swap_num = (upper_b_swap + lower_b_swap)//2
                    # lsqc.pop()
                else: 
                    find_min_swap = True
                    not_solved = False
            else:
                if satisfiable == unsat:
                    core = lsqc.unsat_core()
                    print(core)
                lower_b_swap = bound_swap_num + 1
                if upper_b_swap <= lower_b_swap:
                    # lsqc.pop()
                    # lsqc.add(count_swap <= upper_b_swap)
                    satisfiable = lsqc.check(count_swap <= upper_b_swap)
                    model = lsqc.model()
                    assert(satisfiable == sat)
                    find_min_swap = True
                    not_solved = False
                else:
                    bound_swap_num = (upper_b_swap + lower_b_swap)//2
                    # lsqc.pop()
        return not_solved, model

    def _construct_variable(self, bound_depth, count_qubit_edge):
        # at cycle t, logical qubit q is mapped to pi[q][t]
        pi = [[Int("map_q{}_t{}".format(i, j)) for j in range(bound_depth)]
                for i in range(self.count_program_qubit)]

        # time coordinate for gate l is time[l]
        time = IntVector('time', len(self.list_gate_qubits))

        # space coordinate for gate l is space[l]
        space = IntVector('space', len(self.list_gate_qubits))

        # if at cycle t, a SWAP finishing on edge k, then sigma[k][t]=1
        sigma = [[Bool("ifswap_e{}_t{}".format(i, j))
            for j in range(bound_depth)] for i in range(count_qubit_edge)]

        # if an extra edge e is used, then u[e] = 1
        u = [Bool("u_e{}".format(i)) for i in range(len(self.list_extra_qubit_edge))]

        # for swap optimization
        count_swap = Int('num_swap')

        count_extra_edge = Int('num_extra_edge')
        return pi, time, space, sigma, u, count_swap, count_extra_edge

    def _add_transformation_constraints(self, bound_depth, list_qubit_edge, model, sigma, pi):
        # list_adjacency_qubit takes in a physical qubit index _p_, and
        # returns the list of indices of physical qubits adjacent to _p_
        list_adjacent_qubit = list()
        # list_span_edge takes in a physical qubit index _p_,
        # and returns the list of edges spanned from _p_
        list_span_edge = list()
        count_qubit_edge = len(list_qubit_edge)
        for n in range(self.count_physical_qubit):
            list_adjacent_qubit.append(list())
            list_span_edge.append(list())
        for k in range(count_qubit_edge):
            list_adjacent_qubit[list_qubit_edge[k][0]].append(
                                                        list_qubit_edge[k][1])
            list_adjacent_qubit[list_qubit_edge[k][1]].append(
                                                        list_qubit_edge[k][0])
            list_span_edge[list_qubit_edge[k][0]].append(k)
            list_span_edge[list_qubit_edge[k][1]].append(k)

        # Mapping Not Transformations by SWAP Gates.
        for t in range(bound_depth - 1):
            for n in range(self.count_physical_qubit):
                for m in range(self.count_program_qubit):
                    model.add(
                        Implies(And(sum([If(sigma[k][t], 1, 0)
                            for k in list_span_edge[n]]) == 0,
                                pi[m][t] == n), pi[m][t + 1] == n))
        
        # Mapping Transformations by SWAP Gates.
        for t in range(bound_depth - 1):
            for k in range(count_qubit_edge):
                for m in range(self.count_program_qubit):
                    model.add(Implies(And(sigma[k][t] == True,
                        pi[m][t] == list_qubit_edge[k][0]),
                            pi[m][t + 1] == list_qubit_edge[k][1]))
                    model.add(Implies(And(sigma[k][t] == True,
                        pi[m][t] == list_qubit_edge[k][1]),
                            pi[m][t + 1] == list_qubit_edge[k][0]))

    def _add_injective_mapping_constraints(self, bound_depth, pi, model):
        # Injective Mapping
        for t in range(bound_depth):
            for m in range(self.count_program_qubit):
                model.add(pi[m][t] >= 0, pi[m][t] < self.count_physical_qubit)
                for mm in range(m):
                    model.add(pi[m][t] != pi[mm][t])

    def _add_consistency_gate_constraints(self, bound_depth, list_qubit_edge, pi, space, time, model):
        # Consistency between Mapping and Space Coordinates.
        list_gate_qubits = self.list_gate_qubits
        count_gate = len(list_gate_qubits)
        count_qubit_edge = len(list_qubit_edge)
        list_gate_two = self.list_gate_two
        list_gate_single = self.list_gate_single
        for l in range(count_gate):
            model.add(time[l] >= 0, time[l] < bound_depth)
            if l in list_gate_single:
                model.add(space[l] >= 0, space[l] < self.count_physical_qubit)
                for t in range(bound_depth):
                    model.add(Implies(time[l] == t,
                        pi[list_gate_qubits[l][0]][t] == space[l]))
            elif l in list_gate_two:
                model.add(space[l] >= 0, space[l] < count_qubit_edge)
                for k in range(count_qubit_edge):
                    for t in range(bound_depth):
                        model.add(Implies(And(time[l] == t, space[l] == k),
                            Or(And(list_qubit_edge[k][0] == \
                                    pi[list_gate_qubits[l][0]][t],
                                list_qubit_edge[k][1] == \
                                    pi[list_gate_qubits[l][1]][t]),
                            And(list_qubit_edge[k][1] == \
                                    pi[list_gate_qubits[l][0]][t],
                                list_qubit_edge[k][0] == \
                                    pi[list_gate_qubits[l][1]][t])  )    ))

    def _add_swap_constraints(self, bound_depth, list_qubit_edge, sigma, model, count_swap, normal = False, time = None, space = None):
        # if_overlap_edge takes in two edge indices _e_ and _e'_,
        # and returns whether or not they overlap
        count_qubit_edge = len(list_qubit_edge)
        if_overlap_edge = [[0] * count_qubit_edge
            for k in range(count_qubit_edge)]
        # list_over_lap_edge takes in an edge index _e_,
        # and returnsthe list of edges that overlap with _e_
        list_overlap_edge = list()
        # list_count_overlap_edge is the list of lengths of
        # overlap edge lists of all the _e_
        list_count_overlap_edge = list()
        for k in range(count_qubit_edge):
            list_overlap_edge.append(list())
        for k in range(count_qubit_edge):
            for kk in range(k + 1, count_qubit_edge):
                if (   (list_qubit_edge[k][0] == list_qubit_edge[kk][0]
                        or list_qubit_edge[k][0] == list_qubit_edge[kk][1])
                    or (list_qubit_edge[k][1] == list_qubit_edge[kk][0]
                        or list_qubit_edge[k][1] == list_qubit_edge[kk][1]) ):
                    list_overlap_edge[k].append(kk)
                    list_overlap_edge[kk].append(k)
                    if_overlap_edge[kk][k] = 1
                    if_overlap_edge[k][kk] = 1
        for k in range(count_qubit_edge):
            list_count_overlap_edge.append(len(list_overlap_edge[k]))

        # No swap for t<s
        for t in range(min(self.swap_duration - 1, bound_depth)):
            for k in range(count_qubit_edge):
                model.add(sigma[k][t] == False)
        # swap gates can not overlap with swap
        for t in range(self.swap_duration - 1, bound_depth):
            for k in range(count_qubit_edge):
                for tt in range(t - self.swap_duration + 1, t):
                    model.add(Implies(sigma[k][t] == True,
                        sigma[k][tt] == False))
                for tt in range(t - self.swap_duration + 1, t + 1):
                    for kk in list_overlap_edge[k]:
                        model.add(Implies(sigma[k][t] == True,
                            sigma[kk][tt] == False))

        model.add(
                count_swap == sum([If(sigma[k][t], 1, 0)
                    for k in range(count_qubit_edge)
                        for t in range(bound_depth)]))
        
        if normal:
            # swap gates can not ovelap with other gates
            # the time interval should be modified
            count_gate = len(self.list_gate_qubits)
            for t in range(self.swap_duration - 1, bound_depth):
                for k in range(count_qubit_edge):
                    for l in range(count_gate):
                        for tt in range(t - self.swap_duration + 1, t + self.list_gate_duration[l]):
                            if l in self.list_gate_single:
                                model.add(Implies(And(time[l] == tt,
                                    Or(space[l] == list_qubit_edge[k][0],
                                        space[l] == list_qubit_edge[k][1])),
                                        sigma[k][t] == False             ))
                            elif l in self.list_gate_two:
                                model.add(Implies(And(
                                    time[l] == tt, space[l] == k),
                                        sigma[k][t] == False           ))
                                for kk in list_overlap_edge[k]:
                                    model.add(Implies(And(
                                        time[l] == tt, space[l] == kk),
                                            sigma[k][t] == False       ))

    def _add_edge_constraints(self, bound_depth, count_extra_edge, u, space, sigma, model):
        # record the use of the extra edge
        count_gate = len(self.list_gate_qubits)
        list_extra_qubit_edge = self.list_extra_qubit_edge
        list_extra_qubit_edge_idx = self.list_extra_qubit_edge_idx
        for e in range(len(list_extra_qubit_edge)):
            all_gate = [space[l] == list_extra_qubit_edge_idx[e] for l in range(count_gate)]
            swap_gate = [sigma[list_extra_qubit_edge_idx[e]][t] for t in range(bound_depth - 1)]
            model.add(Or(all_gate + swap_gate) == u[e])
        
        model.add(
            count_extra_edge == sum([If(u[e], 1, 0) for e in range(len(list_extra_qubit_edge))]))

        # add conflict edge use
        for edge_set in self.list_conflict_edge_set:
            if len(edge_set) == 2:
                idx1 = list_extra_qubit_edge_idx.index(self.dict_extra_qubit_edge_idx[edge_set[0]])
                idx2 = list_extra_qubit_edge_idx.index(self.dict_extra_qubit_edge_idx[edge_set[1]])
                model.add(Not(And(u[idx1], u[idx2])))
            else:
                idxs = []
                for edge in edge_set:
                    idxs.append(list_extra_qubit_edge_idx.index(self.dict_extra_qubit_edge_idx[edge]))
                model.add(
                    2 > sum([If(u[idx], 1, 0) for idx in idxs]))                    
                

    def _extract_results(self, model, time, pi, sigma, space, u):
        # post-processing
        list_gate_two = self.list_gate_two
        list_gate_single = self.list_gate_single
        list_qubit_edge = self.list_qubit_edge
        list_gate_qubits = self.list_gate_qubits
        count_qubit_edge = len(list_qubit_edge)
        count_gate = len(list_gate_qubits)
        count_extra_edge = len(self.list_extra_qubit_edge)
        list_gate_name = self.list_gate_name
        count_program_qubit = self.count_program_qubit
        list_extra_qubit_edge_idx = self.list_extra_qubit_edge_idx
        result_time = []
        result_depth = 0
        for l in range(count_gate):
            result_time.append(model[time[l]].as_long())
            result_depth = max(result_depth, result_time[-1])
        result_depth += 1
        list_result_swap = []
        for k in range(count_qubit_edge):
            for t in range(result_depth):
                if model[sigma[k][t]]:
                    list_result_swap.append((k, t))
                    print(f"SWAP on physical edge ({list_qubit_edge[k][0]},"\
                        + f"{list_qubit_edge[k][1]}) at time {t}")
        for l in range(count_gate):
            if len(list_gate_qubits[l]) == 1:
                qq = list_gate_qubits[l][0]
                tt = result_time[l]
                print(f"Gate {l}: {list_gate_name[l]} {qq} on qubit "\
                    + f"{model[pi[qq][tt]].as_long()} at time {tt}")
            else:
                qq = list_gate_qubits[l][0]
                qqq = list_gate_qubits[l][1]
                tt = result_time[l]
                print(f"Gate {l}: {list_gate_name[l]} {qq}, {qqq} on qubits "\
                    + f"{model[pi[qq][tt]].as_long()} and "\
                    + f"{model[pi[qqq][tt]].as_long()} at time {tt}")
        tran_detph = result_depth

        # transition based
        if self.mode == Mode.transition:
            self.swap_duration = self.device.swap_duration
            real_time = [0] * count_gate
            list_depth_on_qubit = [-1] * self.count_physical_qubit
            list_real_swap = []
            for block in range(result_depth):
                for tmp_gate in range(count_gate):
                    if result_time[tmp_gate] == block:
                        qubits = list_gate_qubits[tmp_gate]
                        if len(qubits) == 1:
                            p0 = model[pi[qubits[0]][block]].as_long()
                            real_time[tmp_gate] = \
                                list_depth_on_qubit[p0] + 1
                            list_depth_on_qubit[p0] = \
                                real_time[tmp_gate]
                        else:
                            p0 = model[pi[qubits[0]][block]].as_long()
                            p1 = model[pi[qubits[1]][block]].as_long()
                            real_time[tmp_gate] = max(
                                list_depth_on_qubit[p0],
                                list_depth_on_qubit[p1]) + 1
                            list_depth_on_qubit[p0] = \
                                real_time[tmp_gate]
                            list_depth_on_qubit[p1] = \
                                real_time[tmp_gate]
                            # print(f"{tmp_gate} {p0} {p1} real-time={real_time[tmp_gate]}")

                if block < result_depth - 1:
                    for (k, t) in list_result_swap:
                        if t == block:
                            p0 = list_qubit_edge[k][0]
                            p1 = list_qubit_edge[k][1]
                            tmp_time = max(list_depth_on_qubit[p0],
                                list_depth_on_qubit[p1]) \
                                + self.swap_duration
                            list_depth_on_qubit[p0] = tmp_time
                            list_depth_on_qubit[p1] = tmp_time
                            list_real_swap.append((k, tmp_time))
                # print(list_depth_on_qubit)
            result_time = real_time
            real_depth = 0
            for tmp_depth in list_depth_on_qubit:
                if real_depth < tmp_depth + 1:
                    real_depth = tmp_depth + 1
            result_depth = real_depth
            list_result_swap = list_real_swap
            # print(list_result_swap)

        print(f"result- additional SWAP count = {len(list_result_swap)}.")
        print(f"result- circuit depth = {result_depth}.")

        list_scheduled_gate_qubits = [[] for i in range(result_depth)]
        list_scheduled_gate_name = [[] for i in range(result_depth)]
        for l in range(count_gate):
            t = result_time[l]
            list_scheduled_gate_name[t].append(list_gate_name[l])
            if l in list_gate_single:
                q = model[space[l]].as_long()
                list_scheduled_gate_qubits[t].append((q,))
            elif l in list_gate_two:
                [q0, q1] = list_gate_qubits[l]
                tmp_t = t
                if self.mode == Mode.transition:
                    tmp_t = model[time[l]].as_long()
                q0 = model[pi[q0][tmp_t]].as_long()
                q1 = model[pi[q1][tmp_t]].as_long()
                list_scheduled_gate_qubits[t].append((q0, q1))
            else:
                raise ValueError("Expect single-qubit or two-qubit gate.")

        tmp_depth = result_depth - 1
        if self.mode == Mode.transition:
            tmp_depth = tran_detph - 1
        final_mapping = [model[pi[m][tmp_depth]].as_long() for m in range(count_program_qubit)]

        initial_mapping = [model[pi[m][0]].as_long() for m in range(count_program_qubit)]

        for (k, t) in list_result_swap:
            q0 = list_qubit_edge[k][0]
            q1 = list_qubit_edge[k][1]
            if self.swap_duration == 1:
                list_scheduled_gate_qubits[t].append((q0, q1))
                list_scheduled_gate_name[t].append("SWAP")
            elif self.swap_duration == 3:
                list_scheduled_gate_qubits[t].append((q0, q1))
                list_scheduled_gate_name[t].append("cx")
                list_scheduled_gate_qubits[t - 1].append((q1, q0))
                list_scheduled_gate_name[t - 1].append("cx")
                list_scheduled_gate_qubits[t - 2].append((q0, q1))
                list_scheduled_gate_name[t - 2].append("cx")
            else:
                raise ValueError("Expect SWAP duration one, or three")

        extra_edge = []
        for i in range(count_extra_edge):
            if model[u[i]]:
                extra_edge.append(list_qubit_edge[list_extra_qubit_edge_idx[i]])

        return (result_depth,
                list_scheduled_gate_name,
                list_scheduled_gate_qubits,
                initial_mapping,
                final_mapping,
                extra_edge)
    
    def write_results(self, model, time, pi, sigma, space, u):
        results = self._extract_results(model, time, pi, sigma, space, u)
        D = results[0]
        program_out = ""
        g2 = 0
        g1 = 0
        if self.benchmark == "arith":
            for layer in range(results[0]):
                for gate in range(len(results[1][layer])):
                    if len(results[2][layer][gate]) == 2:
                        program_out += f"{results[1][layer][gate]} {results[2][layer][gate][0]} {results[2][layer][gate][1]}\n"
                        g2 += 1
                    else:
                        program_out += f"{results[1][layer][gate]} {results[2][layer][gate][0]}\n"
                        g1 += 1

        info = dict()
        info["Device_set"] = self.device.name
        info["M"] = self.count_program_qubit
        info["D"] = D
        info["g1"] = g1
        info["g2"] = g2
        info["extra_edge_num"] = len(results[5])
        info["extra_edge"] = results[5]
        info["benchmark"] = self.benchmark
        info["gates"] = results[2]
        info["gate_spec"] = results[1]
        info["initial_mapping"] = results[3]
        info["final_mapping"] = results[4]
        # info["coupling_graph"] = get_char_graph(device_connection)
        if self.mode == Mode.transition:
            info["olsq_mode"] = "transition"
        elif self.mode == Mode.normal:
            info["olsq_mode"] = "normal"
        else:
            info["olsq_mode"] = "mix"
        if self.benchmark == "qcnn":
            info["D"], info["g2"], info["g1"] = cal_QCNN_depth_g2_g1(info["gates"], info["gate_spec"], self.device.count_physical_qubit)
        elif self.benchmark == "qaoa":
            info["D"] = cal_QAOA_depth(info["gates"], info["gate_spec"], self.device.count_physical_qubit)
            nZZ = 0
            nSwap = 0
            for gate_type in info["gate_spec"]:
                for gtype in gate_type:
                    if gtype == "SWAP":
                        nSwap += 1
                    else:
                        nZZ += 1
            info["g2"] = nZZ*2 + nSwap*3
            info["g1"] = nZZ
            # run gate absorption
        # info["cost"] = cal_cost(len(results[5]))
        info['crosstalk'] = cal_crosstalk(info, self.benchmark, self.list_qubit_edge, self.device.count_physical_qubit)
        info['fidelity'], info['fidelity_ct']  = cal_fidelity(info)
        # info['cost-scaled fidelity'], info['cost-scaled fidelity_ct'] = cal_cost_scaled_fidelity(info)
        return info
