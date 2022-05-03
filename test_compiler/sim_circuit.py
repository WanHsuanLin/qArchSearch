import argparse

import csv

SINGLE_QUBIT_GATE_DURATION = 25 #ns
TWO_QUBIT_GATE_DURATION = 10 #ns
MEASUREMENT_DURATION = 4000 #4us

SINGLE_QUBIT_GATE_UNIT = 2
TWO_QUBIT_GATE_UNIT = 1
MEASUREMENT_UNIT = 160
#10ms = 10 000us = 10 000 000 ns=
TIME_LENGTH = 1500

SINGLE_QUBIT_GATE_FID = 0.999
TWO_QUBIT_GATE_FID = 0.991
FACTOR = 0.1
P1_PARALLEL_ERR = 0.005
P2_PARALLEL_ERR = P1_PARALLEL_ERR * FACTOR

T_1=15000
T_PHI=2*T_1


def sim_circuit(phy_qubit_num, data, coupling):
    one_hot_distance, two_hot_distance = preprocess(phy_qubit_num, coupling)
    print("one hot dis:")
    for q in one_hot_distance:
        print(f"qubit {q}:")
        print(one_hot_distance[q])
    print("two hot dis:")
    for q in two_hot_distance:
        print(f"qubit {q}:")
        print(two_hot_distance[q])
    measurement_pair = merge_gate(phy_qubit_num, data)
    qubit_last_time, time_slot_matrix, time_two_qubit_gate_indicator = scheduling(measurement_pair, phy_qubit_num,data)
    calculate_gate_fidelity(data, time_slot_matrix, time_two_qubit_gate_indicator, one_hot_distance, two_hot_distance)
    data["qubit_idling_time"] = calculate_qubit_idling_time(qubit_last_time, time_slot_matrix)
    data["g1"], data["g2"] = calculate_gate_number(data["gate_spec"])
    calculate_cir_fidelity(data)

def calculate_gate_number(gate_spec):
    g1 = 0
    g2 = 0
    for g in gate_spec:
        if g == "sg" or g[0] == "v":
            g1 += 1
        elif g == "syc":
            g2 += 1
    return (g1, g2)

def calculate_cir_fidelity(data):
    fidelity = pow(SINGLE_QUBIT_GATE_FID,data["g1"])
    two_qubit_fidelity_list = data["two_qubit_gates_fidelity"]
    for f in two_qubit_fidelity_list:
        fidelity *= f
    qubit_idling_list = data["qubit_idling_time"]
    for t in qubit_idling_list:
        fidelity *= (1 - ((1/3) * (1/T_1 + 1/T_PHI) * t))
    data["fidelity"] = fidelity
    return fidelity

def calculate_qubit_idling_time(qubit_last_time, time_slot_matrix):
    qubit_idling_time = []
    for q_id, q_last_time in enumerate(qubit_last_time):
        if q_last_time > 0:
            per_q_time_slot = time_slot_matrix[q_id][:q_last_time+1]
            idling_time = per_q_time_slot.count(-1)
            qubit_idling_time.append(idling_time)
    return qubit_idling_time

def calculate_gate_fidelity(data, time_slot_matrix, time_two_qubit_gate_indicator, one_hot_distance, two_hot_distance):
    gate_spec = data["gate_spec"]
    gate_pos = data["gates"]
    gate_fidelity = []
    for time_slot, two_qubit_gate_indictator in zip(time_slot_matrix, time_two_qubit_gate_indicator):
        if two_qubit_gate_indictator:
            for g in time_slot:
                if gate_spec[g] == "syc":
                    g_pos = gate_pos[g]
                    per_gate_fidelity = TWO_QUBIT_GATE_FID
                    for g_p in time_slot:
                        if gate_spec[g_p] == "syc" and g != g_p:
                            g_p_pos = gate_pos[g_p]
                            if g_p_pos[0] in one_hot_distance[g_pos[0]] or g_p_pos[0] in one_hot_distance[g_pos[1]] \
                                or g_p_pos[1] in one_hot_distance[g_pos[0]] or g_p_pos[1] in one_hot_distance[g_pos[1]]:
                                per_gate_fidelity -= P1_PARALLEL_ERR
                            elif g_p_pos[0] in two_hot_distance[g_pos[0]] or g_p_pos[0] in two_hot_distance[g_pos[1]] \
                                or g_p_pos[1] in two_hot_distance[g_pos[0]] or g_p_pos[1] in two_hot_distance[g_pos[1]]:
                                per_gate_fidelity -= P2_PARALLEL_ERR
                    gate_fidelity.append(per_gate_fidelity)
    data["two_qubit_gates_fidelity"] = gate_fidelity

def preprocess(phy_qubit_num, coupling):
    one_hot_distance = dict() # qubit to its one hot dis qubit
    two_hot_distance = dict() # qubit to its two hot dis qubit
    for q in range(phy_qubit_num):
        one_hot_distance[q] = list()
        two_hot_distance[q] = list()
    for edge in coupling:
        one_hot_distance[edge[0]].append(edge[1])
        one_hot_distance[edge[1]].append(edge[0])
    for q in range(phy_qubit_num):
        for neighbor_q in one_hot_distance[q]:
            for two_hot_q in one_hot_distance[neighbor_q]:
                if two_hot_q not in one_hot_distance[q] and two_hot_q != q and two_hot_q not in two_hot_distance[q]:
                    two_hot_distance[q].append(two_hot_q)
    
    return one_hot_distance, two_hot_distance

def scheduling(measurement_pair, phy_qubit_num, data):
    gate_spec = data["gate_spec"]
    gate_pos = data["gates"]
    qubit_last_time = [0] * phy_qubit_num
    time_slot_matrix = [[-1] * TIME_LENGTH ] * phy_qubit_num
    time_two_qubit_gate_indicator = [False] * TIME_LENGTH
    for g_id, (g, g_pos) in enumerate(zip(gate_spec, gate_pos)):
        if g == "sg":
            gate_start_time = qubit_last_time[g_pos[0]] + 1
            for i in range(SINGLE_QUBIT_GATE_UNIT):
                time_slot_matrix[g_pos[0]][gate_start_time+i] = g_id
            qubit_last_time[g_pos[0]] += SINGLE_QUBIT_GATE_UNIT
        elif g == "syc":
            gate_start_time = max(qubit_last_time[g_pos[0]], qubit_last_time[g_pos[1]]) + 1
            for i in range(TWO_QUBIT_GATE_UNIT):
                cur_time = gate_start_time+i
                time_slot_matrix[g_pos[0]][cur_time] = g_id
                time_slot_matrix[g_pos[1]][cur_time] = g_id
                time_two_qubit_gate_indicator[cur_time] = True
            qubit_last_time[g_pos[0]] = cur_time
            qubit_last_time[g_pos[1]] = cur_time
        # v and m may have some problem
        elif g[-2] == "v":
            q_m = gate_pos[measurement_pair[int(g[-1])][0]][0]
            gate_start_time = max(qubit_last_time[g_pos[0]], qubit_last_time[q_m]) + 1
            for i in range(SINGLE_QUBIT_GATE_UNIT):
                time_slot_matrix[g_pos[0]][gate_start_time+i] = g_id
        elif g[-2] == "m":
            gate_start_time = qubit_last_time[g_pos[0]] + 1
            for i in range(MEASUREMENT_UNIT):
                time_slot_matrix[g_pos[0]][gate_start_time+i] = g_id
            continue
            # measurement_pair[1] = g_pos[0]
        else:
            raise ValueError("invalid gate name\n")
    return (qubit_last_time, time_slot_matrix, time_two_qubit_gate_indicator)

def merge_gate(phy_qubit_num, data):
    gate_spec = data["gate_spec"]
    gate_pos = data["gates"]
    new_gate_spec = []
    new_gate_pos = []
    q_last_gate_list = [""]*phy_qubit_num
    measurement_pair = dict()
    # merge consecutive single qubit gates
    g_id = 0
    for g_slot, g_pos_slot in zip(gate_spec, gate_pos):
        for g, g_pos in zip(g_slot, g_pos_slot):
            if g == " U4" or g == " U4 swap" or g == " swap U4" or g == " ZZ swap" or g == " swap ZZ":
                if q_last_gate_list[g_pos[0]] != "sg":
                    new_gate_spec.append("sg")
                    new_gate_pos.append([g_pos[0]])
                if q_last_gate_list[g_pos[1]] != "sg":
                    new_gate_spec.append("sg")
                    new_gate_pos.append([g_pos[1]])
                for _ in range(3):
                    new_gate_spec.append("syc")
                    new_gate_pos.append(g_pos)
                    new_gate_spec.append("sg")
                    new_gate_pos.append([g_pos[0]])
                    new_gate_spec.append("sg")
                    new_gate_pos.append([g_pos[1]])
            elif g == " ZZ":
                new_gate_spec.append("syc")
                new_gate_pos.append(g_pos)
                new_gate_spec.append("sg")
                new_gate_pos.append([g_pos[0]])
                new_gate_spec.append("sg")
                new_gate_pos.append([g_pos[1]])
                new_gate_spec.append("syc")
            elif g == " swap":
                for _ in range(3):
                    new_gate_spec.append("syc")
                    new_gate_pos.append(g_pos)
                    new_gate_spec.append("sg")
                    new_gate_pos.append([g_pos[0]])
                    new_gate_spec.append("sg")
                    new_gate_pos.append([g_pos[1]])
            else:   # measurement and v in qcnn
                index = int(g_pos[-1])
                if not isinstance(measurement_pair[index], list):
                    measurement_pair[index] = [0,0]
                if g[-2] == "v":
                    measurement_pair[index][0] = g_id
                    new_gate_spec.append("v"+str(index))
                    new_gate_pos.append([g_pos[0]])
                elif g[-2] == "m":
                    measurement_pair[index][1] = g_id
                    new_gate_spec.append("m"+str(index))
                    new_gate_pos.append([g_pos[0]])
                else:
                    raise ValueError("invalid gate name\n")
            g_id += 1
            
    data["gate_spec"] = new_gate_spec
    data["gates"] = new_gate_pos
    return measurement_pair

def create_list_from_data(data):
    data_list = []  # create an empty list
    # append the items to the list in the same order.
    data_list.append(data.get('compiler'))
    data_list.append(data.get('fidelity'))
    data_list.append(data.get('g1'))
    data_list.append(data.get('g2'))
    data_list.append(data.get('#e'))
    data_list.append(data.get('idling time'))
    data_list.append(data.get('two qubit gate fidelity'))
    data_list.append(data.get('gates'))
    data_list.append(data.get('gate_spec'))
    data_list.append(data.get('coupling'))
    return data_list


if __name__ == "__main__":
    # # Initialize parser
    # parser = argparse.ArgumentParser()
    # # Adding optional argument
    # parser.add_argument("csv_file", metavar='DS', type=str,
    #     help="csv_file to store gate and gate spec")
    # parser.add_argument("device_set", metavar='DS', type=str,
    #     help="Device: hh: heavy-hexagonal (IBM), grid: sqaure")
    # parser.add_argument("benchmark", metavar='B', type=str,
    #     help="Benchmark Set: arith or qaoa or qcnn")
    # # Read arguments from command line
    # args = parser.parse_args()
    
    # if args.device_set == "hh":
    #     count_physical_qubit = 18
    #     fix_coupling = [[0,4], [1,2], [2,3], [3,4], [4,5], [5,6], [6,7], 
    #                 [2,8], [6,9], [10,11], [8,11], [11,12], [12,13], 
    #                 [13,14], [14,15], [15,16], [9,15], [13,17]]
    # elif args.device_set == "grid":
    #     count_physical_qubit = 16
    #     fix_coupling = [[0,1], [1,2], [2,3], [4,5], [5,6], [6,7], [8,9],
    #     [9,10], [10,11], [12,13], [13,14], [14,15], [0,4], [4,8],
    #     [8,12], [1,5], [5,9], [9,13], [2,6], [6,10], [10,14],
    #     [3,7], [7,11], [11,15]]
    # else:
    #     raise ValueError("invalid benchmark name\n")
    
    # csvreader = csv.reader(args.csv_file)
    # header = []
    # header = next(csvreader)
    # data = dict()

    # csv_name = args.csv_file[:-4]+"_sim.csv"
    # with open(csv_name, 'w+') as c:
    #     writer = csv.writer(c)
    #     writer.writerow(['compiler', 'fidelity', 'g1', 'g2', '#e', 'idling time', 'two qubit gate fidelity', 'gates', 'gate_spec', 'coupling'])

    # for row in csvreader:
    #     data['compiler'] = row[0]
    #     data["gates"] = row[3]
    #     data["gate_spec"] = row[4]
    #     coupling = row[5] + fix_coupling
    #     sim_circuit(count_physical_qubit, data, coupling)
    #     with open(csv_name, 'a') as c:
    #         writer = csv.writer(c)
    #         data_list = create_list_from_data(data)
    #         writer.writerow(data_list)
    
    count_physical_qubit = 16
    coupling = [[0,1], [1,2], [2,3], [4,5], [5,6], [6,7], [8,9],
        [9,10], [10,11], [12,13], [13,14], [14,15], [0,4], [4,8],
        [8,12], [1,5], [5,9], [9,13], [2,6], [6,10], [10,14],
        [3,7], [7,11], [11,15]]
    
    data = dict()
    # data["gates"] = [[[10, 11]], [[13, 14], [9, 10], [7, 11]], [[14, 15], [6, 10]], [[13, 14], [11, 15]]]
    # data["gate_spec"] = [[" ZZ"], [" ZZ", " ZZ", " ZZ swap"], [" swap", " swap"], [" ZZ", " ZZ"]]

    data["gates"] = [[[10, 11]]] 
    data["gate_spec"] = [[" ZZ"]]
    
    sim_circuit(count_physical_qubit, data, coupling)

    