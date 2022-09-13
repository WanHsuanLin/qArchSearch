import datetime

from z3 import Bool, Implies, And, Or, sat, unsat, Solver, set_option, BitVec, ULT, ULE, UGE, BitVecVal, PbLe, Not

from qArchSearch.input import input_qasm
from qArchSearch.device import qcDeviceSet
import math
import pkgutil

TIMEOUT = 90000
# MEMORY_MAX_SIZE = 1000 * 58
MEMORY_MAX_SIZE = 0
MAX_TREAD_NUM = 8
VERBOSE = 0

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

class qArchSearch:
    def __init__(self):
        """Set the objective of OLSQ, and whether it is transition-based

        Args:
            objective_name: can be "depth", "swap", or "fidelity"
        """

        # These values should be updated in setdevice(...)
        self.device = None
        self.count_physical_qubit = 0
        self.list_qubit_edge = []
        self.list_extra_qubit_edge = []
        self.list_basic_qubit_edge = []
        self.list_conflict_edge_set = []
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
        self.bound_depth = 1
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
        print("========================================================================")
        print("=          Domain-Specific Quantum Architectrue Optimization           =")
        print("========================================================================")
        if not self.inpput_dependency:
            self.list_gate_dependency = collision_extracting(self.list_gate_qubits)
        print("[INFO] Using transition based mode...")
        _, results = self._search(False, None, folder, memory_max_size, verbose)
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
        not_solved = True
        start_time = datetime.datetime.now()
        model = None

        # tight_bound_depth: use for depth constraint

        # bound_depth: generate constraints until t = bound_depth
        bound_depth = 8 * self.bound_depth
        while not_solved:
            print("[INFO] Start adding constraints...")
            # variable setting 
            pi, time, space, sigma, u = self._construct_variable(bound_depth, len(list_qubit_edge))

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
            self._add_dependency_constraints(preprossess_only, lsqc, time, bound_depth)

            # # No swap for t<s
            # # swap gates can not overlap with swap
            self._add_swap_constraints(bound_depth, sigma, lsqc, model)
            # Mapping Not Transformations by SWAP Gates.
            # Mapping Transformations by SWAP Gates.
            self._add_transformation_constraints(bound_depth, list_qubit_edge, lsqc, sigma, pi)

            if not preprossess_only:
                # record the use of the extra edge
                self._add_edge_constraints(bound_depth, u, space, sigma, lsqc)
                
            # TODO: iterate each swap num
            tight_depth = None
            for num_e in range(len(self.list_extra_qubit_edge)):
                print(f"[INFO] solving with max number of activate flexible edge = {num_e}")
                per_start = datetime.datetime.now()
                tight_depth, not_solved, result, n_swap = self._optimize_circuit(tight_depth, lsqc, num_e, u, sigma, time, bound_depth, swap_bound, pi, space)
                if not_solved:
                    bound_depth *= 2
                    break
                if preprossess_only:
                    swap_bound = (self.bound_depth-1 , n_swap)
                    break
                if swap_bound != None:
                    swap_bound = (swap_bound[0], n_swap)
                else:
                    swap_bound = (0, n_swap)
                results.append(result)
                print(f"   <RESULT> Compilation time = {datetime.datetime.now() - per_start}.")
                if folder != None:
                    import json
                    with open(f"./{folder}/extra_edge_{num_e}.json", 'w') as file_object:
                        json.dump(results[num_e], file_object)
                if num_e < 4:
                    continue
                if results[-1]['extra_edge_num'] <= results[-2]['extra_edge_num']:
                    break
                
        print(f"   <RESULT> Total compilation time = {datetime.datetime.now() - start_time}.")
        return swap_bound, results

    def _count_swap(self, model, sigma, result_depth):
        n_swap = 0
        for k in range(len(self.list_qubit_edge)):
            for t in range(result_depth):
                if model[sigma[k][t]]:
                    n_swap += 1
        return n_swap

    def _construct_variable(self, bound_depth, count_qubit_edge):
        # at cycle t, logical qubit q is mapped to pi[q][t]
        length = int(math.log2(max(count_qubit_edge, self.count_physical_qubit)))+1
        pi = [[BitVec(("map_q{}_t{}".format(i, j)), length) for j in range(bound_depth)]
                for i in range(self.count_program_qubit)]

        # space coordinate for gate l is space[l]
        space = [BitVec("space{}".format(i), length) for i in range(len(self.list_gate_qubits))]
        
        # time coordinate for gate l is time[l]
        length = int(math.log2(bound_depth))+1
        time = [BitVec("time_{}".format(i), length) for i in range(len(self.list_gate_qubits))]

        


        # if at cycle t, a SWAP finishing on edge k, then sigma[k][t]=1
        sigma = [[Bool("ifswap_e{}_t{}".format(i, j))
            for j in range(bound_depth)] for i in range(count_qubit_edge)]

        # if an extra edge e is used, then u[e] = 1
        u = [Bool("u_e{}".format(i)) for i in range(len(self.list_extra_qubit_edge))]

        return pi, time, space, sigma, u

    def _add_injective_mapping_constraints(self, bound_depth, pi, model):
        # Injective Mapping
        for t in range(bound_depth):
            for m in range(self.count_program_qubit):
                model.add(ULE(0,pi[m][t]), ULT(pi[m][t], self.count_physical_qubit))
                for mm in range(m):
                    model.add(pi[m][t] != pi[mm][t])

    def _add_consistency_gate_constraints(self, bound_depth, list_qubit_edge, pi, space, time, model):
    # def _add_consistency_gate_constraints(self, bound_depth, list_qubit_edge, f_map, space, time, model):
        # Consistency between Mapping and Space Coordinates.
        list_gate_qubits = self.list_gate_qubits
        count_gate = len(list_gate_qubits)
        count_qubit_edge = len(list_qubit_edge)
        list_gate_two = self.list_gate_two
        list_gate_single = self.list_gate_single

        length = int(math.log2(max(count_qubit_edge, self.count_physical_qubit)))+1
        bv_zero = BitVecVal(0, length)
        bv_count_qubit = BitVecVal(self.count_physical_qubit, length)
        bv_count_qubit_edge = BitVecVal(count_qubit_edge, length)


        for l in range(count_gate):
            if l in list_gate_single:
                model.add(ULE(bv_zero, space[l]), ULT(space[l], bv_count_qubit))
                for t in range(bound_depth):
                    model.add(Implies(time[l] == t,
                        pi[list_gate_qubits[l][0]][t] == space[l]))
            elif l in list_gate_two:
                model.add(ULE(bv_zero, space[l]), ULT(space[l], bv_count_qubit_edge))
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

    def _add_swap_constraints(self, bound_depth, list_qubit_edge, sigma, model):
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

        # swap gates can not overlap with swap
        for t in range(bound_depth):
            for k in range(count_qubit_edge):
                # for tt in range(t - self.swap_duration + 1, t):
                #     model.add(Implies(sigma[k][t] == True,
                #         sigma[k][tt] == False))
                for tt in range(t, t + 1):
                    for kk in list_overlap_edge[k]:
                        model.add(Implies(sigma[k][t] == True,
                            sigma[kk][tt] == False))
        

    def _add_dependency_constraints(self, preprossess_only, model, time, bound_depth):
        list_gate_duration = self.list_gate_duration
        list_gate_dependency = self.list_gate_dependency
        count_gate = len(self.list_gate_qubits)
        for d in list_gate_dependency:
            model.add(ULE(time[d[0]],time[d[1]]))

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
                        Implies(And(Not(Or([sigma[k][t] for k in list_span_edge[n]])),
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

    def _add_edge_constraints(self, bound_depth, u, space, sigma, model):
        # record the use of the extra edge
        count_gate = len(self.list_gate_qubits)
        list_extra_qubit_edge = self.list_extra_qubit_edge
        list_extra_qubit_edge_idx = self.list_extra_qubit_edge_idx
        for e in range(len(list_extra_qubit_edge)):
            all_gate = [space[l] == list_extra_qubit_edge_idx[e] for l in range(count_gate)]
            swap_gate = [sigma[list_extra_qubit_edge_idx[e]][t] for t in range(bound_depth - 1)]
            model.add(Or(all_gate + swap_gate) == u[e])
        
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
                model.add(PbLe([(u[idx],1) for idx in idxs], 1) )                  
                

    def _optimize_circuit(self, tight_depth, lsqc, num_e, u, sigma, time, bound_depth, swap_bound, pi, space):
        count_gate = len(self.list_gate_qubits)
        count_qubit_edge = len(self.list_qubit_edge)
        if swap_bound != None:
            print(f"[INFO] optimizing circuit with swap range ({swap_bound[0]},{swap_bound[1]}) ")
            lower_b_swap = swap_bound[0]
            upper_b_swap = swap_bound[1]
        else:
            upper_b_swap = count_gate
            lower_b_swap = 0
        bound_swap_num = 0
        lsqc.push()
        lsqc.add(PbLe([(u[e], 1) for e in range(len(self.list_extra_qubit_edge))], num_e) )
        find_min_depth = False
        # incremental solving use pop and push
        tight_bound_depth = self.bound_depth
        if  tight_depth != None:
            find_min_depth == True
            tight_bound_depth = tight_depth
        if swap_bound != None:
            find_min_depth = True
        while not find_min_depth:
            print("[INFO] Trying maximal depth = {}...".format(tight_bound_depth))
            # for depth optimization
            satisfiable = lsqc.check([UGE(tight_bound_depth, time[l]) for l in range(count_gate)])
            if satisfiable == sat:
                find_min_depth = True
                model = lsqc.model()
                n_swap = self._count_swap(model, sigma, tight_bound_depth)
                upper_b_swap = min(n_swap, upper_b_swap)
                print("[INFO] Find solution with SWAP count = {}...".format(n_swap))

            else:
                # lsqc.pop()
                tight_bound_depth += 1
                if tight_bound_depth > bound_depth:
                    print("[INFO] FAIL to find depth witnin {}.".format(bound_depth))
                    break
        # return tight_bound_depth, False, model, bound_swap_num
        if not find_min_depth:
            lsqc.pop()
            return 0, True, None, 0
        lsqc.add([UGE(tight_bound_depth, time[l]) for l in range(count_gate)])
        # for swap optimization
        find_min_swap = False
        results = None
        while not find_min_swap:
            lsqc.push()
            print("[INFO] Bound of Trying min swap = {}...".format(upper_b_swap))
            lsqc.add(PbLe([(sigma[k][t],1) for k in range(count_qubit_edge)
                         for t in range(bound_depth)], upper_b_swap) )
            satisfiable = lsqc.check()
            if satisfiable == sat:
                model = lsqc.model()
                cur_swap = self._count_swap(model, sigma, tight_bound_depth)
                if upper_b_swap > 0:
                    upper_b_swap -= 1
                    upper_b_swap = min(upper_b_swap, cur_swap)
                else: 
                    find_min_swap = True
                    not_solved = False

                results = self.write_results(model, time, pi, sigma, space, u)
            else:
                find_min_swap = True
                not_solved = False
                bound_swap_num = upper_b_swap + 1
            lsqc.pop()
        lsqc.pop()
        return tight_bound_depth, not_solved, results, bound_swap_num


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
        list_result_swap = []
        result_depth += 1
        for k in range(count_qubit_edge):
            for t in range(result_depth):
                if model[sigma[k][t]]:
                    list_result_swap.append((k, t))
                    print(f"   <RESULT> SWAP on physical edge ({list_qubit_edge[k][0]},"\
                        + f"{list_qubit_edge[k][1]}) at time {t}")
        for l in range(count_gate):
            if len(list_gate_qubits[l]) == 1:
                qq = list_gate_qubits[l][0]
                tt = result_time[l]
                print(f"   <RESULT> Gate {l}: {list_gate_name[l]} {qq} on qubit "\
                    + f"{model[pi[qq][tt]].as_long()} at time {tt}")
            else:
                qq = list_gate_qubits[l][0]
                qqq = list_gate_qubits[l][1]
                tt = result_time[l]
                print(f"   <RESULT> Gate {l}: {list_gate_name[l]} {qq}, {qqq} on qubits "\
                    + f"{model[pi[qq][tt]].as_long()} and "\
                    + f"{model[pi[qqq][tt]].as_long()} at time {tt}")
        tran_detph = result_depth

        # transition based

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
                            + 1
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

        print(f"   <RESULT> - additional SWAP count = {len(list_result_swap)}.")
        print(f"   <RESULT> - circuit depth = {result_depth}.")

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
                tmp_t = model[time[l]].as_long()
                q0 = model[pi[q0][tmp_t]].as_long()
                q1 = model[pi[q1][tmp_t]].as_long()
                list_scheduled_gate_qubits[t].append((q0, q1))
            else:
                raise ValueError("Expect single-qubit or two-qubit gate.")

        tmp_depth = result_depth - 1
        tmp_depth = tran_detph - 1
        final_mapping = [model[pi[m][tmp_depth]].as_long() for m in range(count_program_qubit)]

        initial_mapping = [model[pi[m][0]].as_long() for m in range(count_program_qubit)]

        for (k, t) in list_result_swap:
            q0 = list_qubit_edge[k][0]
            q1 = list_qubit_edge[k][1]
            list_scheduled_gate_qubits[t].append((q0, q1))
            list_scheduled_gate_name[t].append("SWAP")

        extra_edge = []
        for i in range(count_extra_edge):
            if model[u[i]]:
                extra_edge.append(list_qubit_edge[list_extra_qubit_edge_idx[i]])

        # print(list_scheduled_gate_name)
        # print(list_scheduled_gate_qubits)

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
        return info
