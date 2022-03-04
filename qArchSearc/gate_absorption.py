from util import get_list_of_json_files
def compactify(gate_qubits, gate_specs, edges, num_qubits):

    gate_qubits_tmp = list()
    for qubits in gate_qubits:
        q0 = qubits[0]
        q1 = qubits[1]
        gate_qubits_tmp.append((min(q0, q1), max(q0,q1)))
    gate_qubits = gate_qubits_tmp

    result_qubits = list()
    result_specs = list()
   
    incidents = dict()
    for edge in edges:
        incidents[edge] = list()
        q0 = edge[0]
        q1 = edge[1]
        for edgeedge in edges:
            if q0 in edgeedge or q1 in edgeedge:
                if edgeedge != (q0,q1):
                    incidents[edge].append(edgeedge)

    last_edge = [(i,i) for i in range(num_qubits)]
    accu_specs = dict()
    for edge in edges:
        accu_specs[edge] = ''

    for i in range(len(gate_qubits)):
        q0 = gate_qubits[i][0]
        q1 = gate_qubits[i][1]

        if last_edge[q0] != (q0,q0) and last_edge[q1] == (q1,q1):
            result_qubits.append(last_edge[q0])
            result_specs.append(accu_specs[last_edge[q0]])
            accu_specs[last_edge[q0]] = ''
            other_qubit = last_edge[q0][0]
            if other_qubit == q0:
                other_qubit = last_edge[q0][1]
            last_edge[other_qubit] = (other_qubit, other_qubit)
        
        if last_edge[q0] == (q0,q0) and last_edge[q1] != (q1,q1):
            result_qubits.append(last_edge[q1])
            result_specs.append(accu_specs[last_edge[q1]])
            accu_specs[last_edge[q1]] = ''
            other_qubit = last_edge[q1][0]
            if other_qubit == q1:
                other_qubit = last_edge[q1][1]
            last_edge[other_qubit] = (other_qubit, other_qubit)

        
        if last_edge[q0] != (q0,q0) and last_edge[q1] != (q1,q1):
            if last_edge[q0] != (q0,q1) and last_edge[q1] != (q0,q1):
                result_qubits.append(last_edge[q0])
                result_specs.append(accu_specs[last_edge[q0]])
                accu_specs[last_edge[q0]] = ''
                other_qubit = last_edge[q0][0]
                if other_qubit == q0:
                    other_qubit = last_edge[q0][1]
                last_edge[other_qubit] = (other_qubit, other_qubit)

                result_qubits.append(last_edge[q1])
                result_specs.append(accu_specs[last_edge[q1]])
                accu_specs[last_edge[q1]] = ''
                other_qubit = last_edge[q1][0]
                if other_qubit == q1:
                    other_qubit = last_edge[q1][1]
                last_edge[other_qubit] = (other_qubit, other_qubit)

        last_edge[q0] = (q0,q1)
        last_edge[q1] = (q0,q1)
        accu_specs[(q0,q1)] += " " + gate_specs[i]


    rest_gate_qubits = list()
    rest_gate_specs = list()
    for rest_gate in last_edge:
        if rest_gate not in rest_gate_qubits:
            if rest_gate[0] != rest_gate[1]:
                rest_gate_qubits.append(rest_gate)
                rest_gate_specs.append(accu_specs[rest_gate])
    for spec in rest_gate_specs:
        spec = spec.replace(" swap swap", "")
    for j, qubits in enumerate(rest_gate_qubits):
        if rest_gate_specs[j] != "" and rest_gate_specs[j] != " swap":
            result_qubits.append(rest_gate_qubits[j])
            result_specs.append(rest_gate_specs[j])
        if rest_gate_specs[j] == " swap":
            print(f"final swap on qubits {qubits[0]} and {qubits[1]}")


    for spec in result_specs:
        spec = spec.replace(" swap swap", "")
    
    return [result_qubits, result_specs]

def push_left_layers(result_qubits, result_specs, num_qubits, ifprint=False):

    for qubits in result_qubits:
        q0 = qubits[0]
        q1 = qubits[1]
        if q0 > q1:
            qubits = (q1, q0)

    layers_qubits = list()
    layers_qubits.append(list())
    layers_specs = list()
    layers_specs.append(list())
    last_layer = [-1 for _ in range(num_qubits)]
    for j, gate in enumerate(result_qubits):
        if result_specs[j] != "":
            this_layer = max(last_layer[gate[0]], last_layer[gate[1]]) + 1
            if this_layer == 0 and result_qubits[j] == " swap":
                print(f"initial swap on qubits {gate[0]} and {gate[1]}")
                continue
            last_layer[gate[0]] = this_layer
            last_layer[gate[1]] = this_layer
            if this_layer + 1 > len(layers_qubits):
                layers_qubits.append(list())
                layers_specs.append(list())
            layers_qubits[this_layer].append(gate)
            layers_specs[this_layer].append(result_specs[j])

    if ifprint:
        for j in range(len(layers_qubits)):
            print("layer " + str(j) + "---------------------------------")
            for k in range(len(layers_qubits[j])):
                print("gate (" + layers_specs[j][k] + ") on qubits (" +
                    str(layers_qubits[j][k][0]) + " " +
                    str(layers_qubits[j][k][1]) + ")")

        print("metric-----------------------------------")
        depth = len(layers_qubits)
        print("depth " + str(depth))
        swap_count = 0
        for spec in result_specs:
            if spec == " swap":
                swap_count += 1
        print("#swap " + str(swap_count))

    return [depth, swap_count, layers_qubits, layers_specs]

def layer_error(qubit_pairs, specs, edges):
    for i in range(len(specs)):
        p0 = qubit_pairs[i][0]
        p1 = qubit_pairs[i][1]
        if (not ((p0,p1) in edges)) and (not ((p1,p0) in edges)):
            print(f"spotted a bug: {specs[i]} on {p0} and {p1}")
            return True
    return False

def filter_mapping(original_pairs, specs, original_mapping, new_mapping):
    new_pairs = list()
    for i in range(len(specs)):
        if specs[i] != 'SWAP' and specs[i] != 'swap':
            p0 = original_pairs[i][0]
            p1 = original_pairs[i][1]
            new_p0 = -1
            new_p1 = -1

            for q in range(len(original_mapping)):
                if original_mapping[q] == p0:
                    new_p0 = new_mapping[q]
                if original_mapping[q] == p1:
                    new_p1 = new_mapping[q]
            new_pairs.append([new_p0, new_p1])
        else:
            new_pairs.append(original_pairs[i])
    return new_pairs

def correct_bug(gate_qubits, gate_specs, edges, initial_mapping):
    
    results = list()
    results.append(0)

    # get all the mapping
    all_mapping = list()
    all_mapping.append(initial_mapping)
    for i in range(1, len(gate_qubits)):
        this_mapping = list(all_mapping[i-1])
        for j in range(len(gate_qubits[i-1])):
            if gate_specs[i-1][j] == 'SWAP' or gate_specs[i-1][j] == 'swap':
                p0 = gate_qubits[i-1][j][0]
                p1 = gate_qubits[i-1][j][1]
                for k in range(len(all_mapping[i-1])):
                    p = all_mapping[i-1][k]
                    if p == p0:
                        this_mapping[k] = p1
                    elif p == p1:
                        this_mapping[k] = p0
        all_mapping.append(this_mapping)
    
    # fixing errors
    for i in range(len(gate_qubits)):
        if layer_error(gate_qubits[i], gate_specs[i], edges):
            results[0] = -1
            for j in range(i+1, len(gate_qubits)):
                trial_pairs = filter_mapping(gate_qubits[i], gate_specs[i],
                    all_mapping[j], all_mapping[i])
                if not layer_error(trial_pairs, gate_specs[i], edges):
                    gate_qubits[i] = trial_pairs
                    break

    results.append(gate_qubits)
    return results     


def example():
    from olsq import OLSQ
    from olsq.device import qcdevice


    coupling_graph = [(0,1), (1,2), (2,3), (4,5), (5,6), (6,7), (8,9),
            (9,10), (10,11), (12,13), (13,14), (14,15), (0,4), (4,8),
            (8,12), (1,5), (5,9), (9,13), (2,6), (6,10), (10,14),
            (3,7), (7,11), (11,15)]
    qv_num = 5
    u4_qubits = [(0,1), (2,3), (0,3), (1,4), (4,1), (2,0), (2,4), (1,3), (2,3), (1,4)]

    # solve qubit mapping for the circuit
    lsqc_solver = OLSQ(objective_name='swap', mode='transition')

    lsqc_solver.setdevice(qcdevice(name='arch0', nqubits=16,
    connection=coupling_graph, swap_duration=1))

    program = [qv_num, u4_qubits, ['U4' for _ in range(len(u4_qubits))]]
    lsqc_solver.setprogram(program, "IR")

    results = lsqc_solver.solve(output_mode="IR")
    # print(results)
    tmp_qubits = list()
    tmp_params = list()
    for i in range(results[0]):
        tmp_qubits += results[2][i]
        for param in results[1][i]:
            if param == 'SWAP':
                tmp_params.append('swap')
            else:
                tmp_params.append(param)

    tmp1_qubits, tmp1_params = compactify(tmp_qubits, tmp_params, coupling_graph, 16)
    depth, _, u4gate_qubits, u4gate_params = push_left_layers(tmp1_qubits, tmp1_params, 16, True)
    return 0

# example()
# QV-128: [(3, 1), (4, 2), (0, 6), (1, 5), (0, 2), (6, 3), (2, 1), (5, 0), (4, 6), (0, 3), (1, 6), (4, 5), (0, 4), (1, 6), (5, 2), (4, 2), (3, 5), (6, 0), (5, 1), (0, 3), (6, 4)]
# QV-256: [(7, 1), (2, 3), (4, 5), (0, 6), (2, 5), (7, 3), (6, 4), (1, 0), (1, 2), (0, 4), (6, 7), (3, 5), (0, 4), (2, 3), (5, 1), (7, 6), (7, 6), (1, 3), (4, 0), (5, 2), (1, 4), (6, 2), (5, 3), (0, 7), (4, 6), (2, 1), (0, 5), (3, 7), (2, 3), (0, 7), (5, 1), (4, 6)]
# QV-512: [(8, 4), (5, 1), (0, 2), (3, 7), (2, 7), (8, 6), (1, 0), (5, 4), (0, 4), (1, 3), (8, 7), (6, 2), (6, 3), (8, 7), (5, 1), (2, 4), (8, 1), (4, 7), (0, 6), (2, 3), (8, 5), (4, 3), (2, 7), (1, 0), (3, 6), (0, 4), (1, 7), (8, 5), (4, 8), (3, 1), (7, 0), (5, 2), (6, 0), (4, 7), (1, 5), (2, 8)]


# correcting bug example
# coupling_graph = [(0,1), (1,2), (2,3), (4,5), (5,6), (6,7), (8,9),
#         (9,10), (10,11), (12,13), (13,14), (14,15), (0,4), (4,8),
#         (8,12), (1,5), (5,9), (9,13), (2,6), (6,10), (10,14),
#         (3,7), (7,11), (11,15)] + [(1,6), (10, 13)]

# result = correct_bug([[[5, 4], [10, 9]], [[5, 1], [10, 6], [4, 0]], [[1, 2], [5, 9]], [[9, 10], [5, 4], [2, 0]], [[5, 6], [1, 2]], [[1, 0]], [[1, 6]]],
# [["ZZ", "ZZ"], ["ZZ", "ZZ", "ZZ"], ["ZZ", "SWAP"], ["ZZ", "ZZ", "ZZ"], ["ZZ", "SWAP"], ["ZZ"], ["ZZ"]],
# coupling_graph, [4, 6, 5, 9, 10, 1, 0, 2])

# print("finish fixing")
# print(result[0])
# print(result[1])


def get_coupling_graph(device: int):
    my_coupling = [(0,1), (1,2), (2,3), (4,5), (5,6), (6,7), (8,9),
        (9,10), (10,11), (12,13), (13,14), (14,15), (0,4), (4,8),
        (8,12), (1,5), (5,9), (9,13), (2,6), (6,10), (10,14),
        (3,7), (7,11), (11,15)]
    
    tmp = device
    if tmp % 2 == 1:
        my_coupling += [(0,5), (3,6), (9,12), (10,15)]
    tmp = tmp // 2
    if tmp % 2 == 1:
        my_coupling += [(1,4), (2,7), (8,13), (11,14)]
    tmp = tmp // 2
    if tmp % 2 == 1:
        my_coupling += [(1,6), (10, 13)]
    tmp = tmp // 2
    if tmp % 2 == 1:
        my_coupling += [(2,5), (9,14)]
    tmp = tmp // 2
    if tmp % 2 == 1:
        my_coupling += [(4,9), (7,10)]
    tmp = tmp // 2
    if tmp % 2 == 1:
        my_coupling += [(5,8), (6,11)]
    tmp = tmp // 2
    if tmp % 2 == 1:
        my_coupling += [(5,10)]
    tmp = tmp // 2
    if tmp % 2 == 1:
        my_coupling += [(6,9)]

    return my_coupling

def get_ibm_coupling_graph(device:str):
    my_coupling = []
    num_qubit = 0
    if device == "p1":
        num_qubit = 20
        my_coupling = [(0,1),(1,2),(3,4),(5,6),(6,7),(8,9),(10,11),(11,12),(12,13),(13,14),(15,16),(16,17),(17,18),(18,19),
                        (0,5),(1,6),(2,7),(4,9),(5,10),(6,11),(7,12),(8,13),(9,14),(10,15),(11,16),(12,17),(14,19),
                        (1,7),(2,6),(3,9),(4,8),(5,11),(6,10),(7,13),(8,12),(11,17),(12,16),(13,19),(14,18)]
    elif device == "p2":
        num_qubit = 20
        my_coupling = [(0,1),(1,2),(2,3),(3,4),(5,6),(6,7),(7,8),(8,9),(10,11),(11,12),(12,13),(13,14),(15,16),(16,17),(18,19),
                        (0,5),(1,6),(4,9),(5,10),(6,11),(7,12),(8,13),(10,15),(11,16),(14,19),
                        (1,7),(2,6),(3,9),(4,8),(5,11),(6,10),(7,13),(8,12),(11,17),(12,16),(13,19),(14,18)]
    elif device == "p3":
        num_qubit = 20
        my_coupling = [(0,1),(1,2),(2,3),(3,4),(5,6),(6,7),(7,8),(8,9),(10,11),(11,12),(12,13),(13,14),(15,16),(16,17),(17,18),(18,19),
                        (0,5),(4,9),(5,10),(7,12),(9,14),(10,15),(14,19)]
    elif device == "p4":
        num_qubit = 20
        my_coupling = [(0,1),(1,2),(2,3),(3,4),(5,6),(6,7),(7,8),(8,9),(10,11),(11,12),(12,13),(13,14),(15,16),(16,17),(17,18),(18,19),
                        (1,6),(3,8),(5,10),(7,12),(9,14),(11,16),(13,18)]
    elif device == "f4":
        num_qubit = 27
        my_coupling = [(0,1),(1,2),(2,3),(3,5),(5,6),(6,7),(7,8),(8,10),(10,11),(13,14),(13,15),(15,16),(16,18),(18,20),(20,21),(21,22),(22,24),(24,25),
                        (1,26),(25,26),(3,4),(8,9),(11,12),(12,13),(16,17),(6,19),(19,20),(22,23)]
    return num_qubit, my_coupling


def calQCNNDepthG2G1(gates:list,gate_spec:list,num_qubit:int):
    d = [0] * num_qubit
    cg = ["swap"] * num_qubit
    g2 = 0
    g1 = 0
    for gate_pos, gate_type in zip(gates,gate_spec):
        for pos, gtype in zip(gate_pos, gate_type):
            g2 += 3
            # print(pos)
            gtype = gtype.lstrip().lstrip()
            # print(gtype)
            
            if gtype == "swap":
                d[pos[0]] = max(d[pos[0]],d[pos[1]])+3
            else:
                gtype = "U4"
                if cg[pos[0]] == cg[pos[1]]:
                    if cg[pos[0]] == "swap":
                        g1 += 7
                        d[pos[0]] = max(d[pos[0]],d[pos[1]])+7
                    elif cg[pos[0]] == "U4":
                        g1 += 5
                        d[pos[0]] = max(d[pos[0]],d[pos[1]])+6
                    else:
                        assert(False)
                elif (cg[pos[0]] == "swap") and (cg[pos[1]] == "U4"):
                    d[pos[0]] = max(d[pos[0]]+7,d[pos[1]]+6)
                    if d[pos[0]]+7 > d[pos[1]]+6:
                        g1 += 7
                    else:
                        g1 += 5
                elif (cg[pos[0]] == "U4") and (cg[pos[1]] == "swap"):
                    g1 += 7
                    d[pos[0]] = max(d[pos[0]]+6,d[pos[1]]+7)
                    if d[pos[0]]+6 > d[pos[1]]+7:
                        g1 += 7
                    else:
                        g1 += 5
                else:
                    assert (False)
            # else:
            #     assert(False)
            d[pos[1]] = d[pos[0]]
            cg[pos[0]] = gtype
            cg[pos[1]] = gtype
    return [max(d), g2, g1]

def calQAOADepthG2G1(gates:list,gate_spec:list,num_qubit:int):
    d = [0] * num_qubit
    cg = ["swap"] * num_qubit
    for gate_pos, gate_type in zip(gates,gate_spec):
        for pos, gtype in zip(gate_pos, gate_type):
            # print(pos)
            gtype = gtype.lstrip().lstrip()
            # print(gtype)
            
            if gtype == "swap" or gtype == "ZZ" or gtype == "ZZ ZZ":
                d[pos[0]] = max(d[pos[0]],d[pos[1]])+3
            elif gtype == "ZZ swap":
                d[pos[0]] = max(d[pos[0]],d[pos[1]])+4
            else:
                assert(False)
            d[pos[1]] = d[pos[0]]
            cg[pos[0]] = gtype
            cg[pos[1]] = gtype
    return max(d)

if __name__ == "__main__":
    import argparse
    import json
    parser = argparse.ArgumentParser()
    # Adding optional argument
    parser.add_argument("folder", metavar='folder', type=str,
        help="Result Folder: each benchmark result")
    parser.add_argument("benchmark", metavar='B', type=str,
        help="Benchmark Set: arith or qaoa or qcnn")
    args = parser.parse_args()
    list_of_files = get_list_of_json_files(args.folder)
    for file in list_of_files:
        print(file)
        with open(file) as f:
            data = json.load(f)
        coupling_graph = get_coupling_graph(data["device"])
        num_qubit = 16
        # num_qubit, coupling_graph = get_ibm_coupling_graph(data["device"])
        # print('before correction')
        # print(data["gates"])
        # print('---')

        result = correct_bug(data["gates"],data["gate_spec"],coupling_graph,data["initial_mapping"])
        data["gates"] = result[1]

        # print('finish correction')
        # print(result[1])
        # print('---')

        tmp_qubits = list()
        tmp_params = list()
        for gate_pos, gate_type in zip(data["gates"],data["gate_spec"]):
            tmp_qubits += gate_pos
            for gtype in gate_type:
                if gtype == "SWAP":
                    tmp_params.append('swap')
                else:
                    if args.benchmark == "qaoa":
                        tmp_params.append('ZZ') #U4
                    else:
                        tmp_params.append("U4")
        
        # for i in range(results[0]):
        #     tmp_qubits += results[2][i]
        #     for param in results[1][i]:
        #         if param == 'SWAP':
        #             tmp_params.append('swap')
        #         else:
        #             tmp_params.append(param)
        # print(tmp_qubits)
        # print(tmp_params)

        tmp1_qubits, tmp1_params = compactify(tmp_qubits, tmp_params, coupling_graph, num_qubit)
        depth, swap_count, u4gate_qubits, u4gate_params = push_left_layers(tmp1_qubits, tmp1_params, num_qubit, True)

        data["gates"] = u4gate_qubits
        data["gate_spec"] = u4gate_params
        if args.benchmark == "qaoa":
            data["D"] = depth*3
            nZZ = (len(tmp1_params)-swap_count)
            data["g2"] = nZZ*2 + swap_count*3
            data["g1"] = nZZ
        elif args.benchmark == "qcnn":
            print(data["gates"])
            print(data["gate_spec"])
            data["D"], data["g2"], data["g1"] = calQCNNDepthG2G1(data["gates"], data["gate_spec"], num_qubit)
        print("------------")
        print(data["D"])

        with open(file, 'w+') as f:
            json.dump(data, f)
    
        # print(results)
        
