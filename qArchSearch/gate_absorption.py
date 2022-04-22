from qArchSearch.olsq.util import cal_QCNN_depth_g2_g1, cal_QAOA_depth

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

def run_gate_absorption(benchmark:str, data, coupling_graph:list, num_qubit):
    # num_qubit = 16
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
                if benchmark == "qaoa":
                    tmp_params.append('ZZ') #U4
                else:
                    tmp_params.append("U4")

    tmp1_qubits, tmp1_params = compactify(tmp_qubits, tmp_params, coupling_graph, num_qubit)
    depth, swap_count, u4gate_qubits, u4gate_params = push_left_layers(tmp1_qubits, tmp1_params, num_qubit, True)

    data["gates"] = u4gate_qubits
    data["gate_spec"] = u4gate_params
    if benchmark == "qaoa":
        data["D"] = cal_QAOA_depth(data["gates"], data["gate_spec"], num_qubit)
        nZZ = (len(tmp1_params)-swap_count)
        data["g2"] = nZZ*2 + swap_count*3
        data["g1"] = nZZ
    elif benchmark == "qcnn":
        data["D"], data["g2"], data["g1"] = cal_QCNN_depth_g2_g1(data["gates"], data["gate_spec"], num_qubit)

    
