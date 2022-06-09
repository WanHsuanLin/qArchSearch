# python3 test_compiler/sim_circuit.py results_diff_compiler/grid/qcnn/grid_optimal_8_0.csv grid qaoa
import argparse

import csv
import numpy as np
import ast

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
T_PHI=25000


def sim_circuit(phy_qubit_num, data, coupling, measure_at_end = True):
    one_hot_distance, two_hot_distance = preprocess(phy_qubit_num, coupling)
    # print("one hot dis:")
    # for q in one_hot_distance:
    #     print(f"qubit {q}:")
    #     print(one_hot_distance[q])
    # print("two hot dis:")
    # for q in two_hot_distance:
    #     print(f"qubit {q}:")
    #     print(two_hot_distance[q])
    # print("ori gate info:")
    # print("gate_spec:")
    # print(data["gate_spec"])
    # print("gate_pos:")
    # print(data["gates"])
    measurement_pair = merge_gate(phy_qubit_num, data)
    # print("\nnew gate info:")
    # print("gate_spec:")
    # print(data["gate_spec"])
    # print("gate_pos:")
    # print(data["gates"])
    qubit_last_time, time_slot_matrix, time_two_qubit_gate_indicator = scheduling(measurement_pair, phy_qubit_num,data)
    # print("qubit_last_time:")
    # print(qubit_last_time)
    
    # print("circuit_depth ", circuit_d)
    # print("time_two_qubit_gate_indicator:")
    # print(time_two_qubit_gate_indicator[:circuit_d + 2])
    # print("gate scheduling:")
    # for qubit in range(phy_qubit_num):
    #     print(time_slot_matrix[qubit][:circuit_d + 2])
    calculate_gate_fidelity(data, time_slot_matrix, time_two_qubit_gate_indicator, one_hot_distance, two_hot_distance)
    # print("two_qubit_gates_fidelity:")
    # print(data["two_qubit_gates_fidelity"])
    # data["qubit_idling_time"] = calculate_qubit_idling_time(qubit_last_time, time_slot_matrix, measure_at_end)
    new_calculate_qubit_idling_time(data, phy_qubit_num, qubit_last_time, time_slot_matrix, measure_at_end)
    # print("qubit_idling_time:")
    # print(data["qubit_idling_time"])
    data["g1"], data["g2"] = calculate_gate_number(data["gate_spec"])
    assert(data["g2"] == len(data["two_qubit_gates_fidelity"]))
    # print("g1: ", data["g1"])
    calculate_cir_fidelity(data)
    # print("fidelity: ", data["fidelity"])

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
    # fidelity = 1
    fidelity  = pow(SINGLE_QUBIT_GATE_FID,data["g1"])
    qubit_idling_list = data["qubit_idling_time"]
    for t in qubit_idling_list:
        fidelity *= (1 - ((1/3) * (1/T_1 + 1/T_PHI) * t))
    # print(fidelity)
    fidelity_no_crosstalk = fidelity * pow(TWO_QUBIT_GATE_FID,data["g2"])
    two_qubit_fidelity_list = data["two_qubit_gates_fidelity"]
    assert(len(two_qubit_fidelity_list)==data["g2"])
    for f in two_qubit_fidelity_list:
        fidelity *= f

    data["fidelity"] = fidelity
    # print("fidelity: ", fidelity)
    # print("fidelity_no_crosstalk: ", fidelity_no_crosstalk)
    data['fidelity_no_crosstalk'] = fidelity_no_crosstalk

def calculate_qubit_idling_time(qubit_last_time, time_slot_matrix, measure_at_end):
    qubit_idling_time = []

    if measure_at_end:
        circuit_depth = max(qubit_last_time)
    for q_id, q_last_time in enumerate(qubit_last_time):
        if q_last_time > 0:
            if measure_at_end:
                per_q_time_slot = time_slot_matrix[q_id][:circuit_depth+1]
            else:
                per_q_time_slot = time_slot_matrix[q_id][:q_last_time+1]
            idling_time = per_q_time_slot.count(-1) - 1
            # print(idling_time)
            qubit_idling_time.append(idling_time)

    data['D'] = max(qubit_last_time)
    data['qubit_lifetime'] = qubit_last_time
    return qubit_idling_time

def new_calculate_qubit_idling_time(data, phy_qubit_num, qubit_last_time, time_slot_matrix, measure_at_end):

    max_d =  max(qubit_last_time)
    gate_spec = data["gate_spec"]
    affective_q = []
    for q_id, q_last_time in enumerate(qubit_last_time):
        if q_last_time > 0:
            affective_q.append(q_id)

    qubit_idling_time = [0] * phy_qubit_num
    qubit_lifetime = [0] * phy_qubit_num

    for time in range(1,max_d):
        has_single_qubit_gate = False
        has_measurement = False
        for q in affective_q:
            if time_slot_matrix[q][time] == -1:
                continue
            gate_name = gate_spec[time_slot_matrix[q][time]]
            if gate_name == "sg" or gate_name[0] == "v":
                has_single_qubit_gate = True
            elif gate_name[0] == "m":
                has_measurement = True
                break
        for q in affective_q:
            if not measure_at_end and qubit_last_time[q] < time:
                continue
            if has_measurement:
                qubit_lifetime[q] += MEASUREMENT_DURATION
            elif has_single_qubit_gate: 
                qubit_lifetime[q] += SINGLE_QUBIT_GATE_DURATION
            else:
                qubit_lifetime[q] += TWO_QUBIT_GATE_DURATION
            
            if time_slot_matrix[q][time] == -1:
                if has_measurement:
                    qubit_idling_time[q] += MEASUREMENT_DURATION
                elif has_single_qubit_gate:
                    qubit_idling_time[q] += SINGLE_QUBIT_GATE_DURATION
                else:
                    qubit_idling_time[q] += TWO_QUBIT_GATE_DURATION
            else:
                gate_name = gate_spec[time_slot_matrix[q][time]]
                if gate_name == "sg" or gate_name[0] == "v":
                    if has_measurement:
                        qubit_idling_time[q] += (MEASUREMENT_DURATION-SINGLE_QUBIT_GATE_DURATION)
                elif gate_name == "syc":
                    if has_measurement:
                        qubit_idling_time[q] += (MEASUREMENT_DURATION-TWO_QUBIT_GATE_DURATION)
                    elif has_single_qubit_gate:
                        qubit_idling_time[q] += (SINGLE_QUBIT_GATE_DURATION-TWO_QUBIT_GATE_DURATION)
    data['D'] = max(qubit_lifetime)
    data['qubit_lifetime'] = list()
    data['qubit_idling_time'] = list()
    for lifetime, idling_time in zip (qubit_lifetime, qubit_idling_time):
        if lifetime > 0:
            data["qubit_idling_time"].append(idling_time)
            data["qubit_lifetime"].append(lifetime)

def calculate_gate_fidelity(data, time_slot_matrix, time_two_qubit_gate_indicator, one_hot_distance, two_hot_distance):
    gate_spec = data["gate_spec"]
    gate_pos = data["gates"]
    gate_fidelity = []
    two_qubit_gate_set = set()
    transpose_time_slot_matrix = np.array(time_slot_matrix).T.tolist()
    for time_slot, two_qubit_gate_indictator in zip(transpose_time_slot_matrix, time_two_qubit_gate_indicator):
        if two_qubit_gate_indictator:
            # print("in a time slot")
            # print(time_slot)
            for g in time_slot:
                if g != -1 and gate_spec[g] == "syc" and g not in two_qubit_gate_set:
                    # print(f"check gate {g}")
                    checked_set = set()
                    g_pos = gate_pos[g]
                    per_gate_fidelity = TWO_QUBIT_GATE_FID
                    for g_p in time_slot:
                        if g_p != -1 and gate_spec[g_p] == "syc" and g != g_p and g_p not in checked_set:
                            g_p_pos = gate_pos[g_p]
                            if g_p_pos[0] in one_hot_distance[g_pos[0]] or g_p_pos[0] in one_hot_distance[g_pos[1]] \
                                or g_p_pos[1] in one_hot_distance[g_pos[0]] or g_p_pos[1] in one_hot_distance[g_pos[1]]:
                                per_gate_fidelity -= P1_PARALLEL_ERR
                            elif g_p_pos[0] in two_hot_distance[g_pos[0]] or g_p_pos[0] in two_hot_distance[g_pos[1]] \
                                or g_p_pos[1] in two_hot_distance[g_pos[0]] or g_p_pos[1] in two_hot_distance[g_pos[1]]:
                                per_gate_fidelity -= P2_PARALLEL_ERR
                            checked_set.add(g_p)
                    # print(f"result fid = {per_gate_fidelity}")
                    gate_fidelity.append(per_gate_fidelity)
                    two_qubit_gate_set.add(g)
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
    time_slot_matrix = [] 
    for _ in range(phy_qubit_num):
        time_slot_matrix.append([-1] * TIME_LENGTH )
    time_two_qubit_gate_indicator = [False] * TIME_LENGTH
    for g_id, (g, g_pos) in enumerate(zip(gate_spec, gate_pos)):
        if g == "sg":
            gate_start_time = qubit_last_time[g_pos[0]] + 1
            # for i in range(SINGLE_QUBIT_GATE_UNIT):
            #     time_slot_matrix[g_pos[0]][gate_start_time+i] = g_id
            # qubit_last_time[g_pos[0]] += SINGLE_QUBIT_GATE_UNIT
            time_slot_matrix[g_pos[0]][gate_start_time] = g_id
            qubit_last_time[g_pos[0]] += 1
        elif g == "syc":
            print
            gate_start_time = max(qubit_last_time[g_pos[0]], qubit_last_time[g_pos[1]]) + 1
            # for i in range(TWO_QUBIT_GATE_UNIT):
            #     cur_time = gate_start_time+i
            #     time_slot_matrix[g_pos[0]][cur_time] = g_id
            #     time_slot_matrix[g_pos[1]][cur_time] = g_id
            #     time_two_qubit_gate_indicator[cur_time] = True
            # qubit_last_time[g_pos[0]] = cur_time
            # qubit_last_time[g_pos[1]] = cur_time
            time_slot_matrix[g_pos[0]][gate_start_time] = g_id
            time_slot_matrix[g_pos[1]][gate_start_time] = g_id
            time_two_qubit_gate_indicator[gate_start_time] = True
            qubit_last_time[g_pos[0]] = gate_start_time
            qubit_last_time[g_pos[1]] = gate_start_time
        # v and m may have some problem
        elif g[0] == "v":
            q_m = gate_pos[measurement_pair[int(g[1:])][0]][0]
            gate_start_time = max(qubit_last_time[g_pos[0]], qubit_last_time[q_m]) + 1
            time_slot_matrix[g_pos[0]][gate_start_time] = g_id
            qubit_last_time[g_pos[0]] = gate_start_time
            # print("measurement_pair :", measurement_pair[int(g[1:])], " , time: ", qubit_last_time[q_m])
            # print("max time: ", gate_start_time)
            # for i in range(SINGLE_QUBIT_GATE_UNIT):
            #     time_slot_matrix[g_pos[0]][gate_start_time+i] = g_id
            # qubit_last_time[g_pos[0]] = gate_start_time+SINGLE_QUBIT_GATE_UNIT
        elif g[0] == "m":
            gate_start_time = qubit_last_time[g_pos[0]] + 1
            # for i in range(MEASUREMENT_UNIT):
            #     time_slot_matrix[g_pos[0]][gate_start_time+i] = g_id
            # qubit_last_time[g_pos[0]] = gate_start_time+MEASUREMENT_UNIT
            time_slot_matrix[g_pos[0]][gate_start_time] = g_id
            qubit_last_time[g_pos[0]] += 1
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
    # print(gate_spec)
    for g_slot, g_pos_slot in zip(gate_spec, gate_pos):
        for g, g_pos in zip(g_slot, g_pos_slot):
            # print(g)
            # print(g_pos)
            if g == "U4" or g == " U4 U4" or g == " U4" or g == " U4 swap" or g == " swap U4" or g == " ZZ swap" or g == " swap ZZ":
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
                q_last_gate_list[g_pos[0]] = "sg"
                q_last_gate_list[g_pos[1]] = "sg"
            elif g == " ZZ" or g == "ZZ":
                new_gate_spec.append("syc")
                new_gate_pos.append(g_pos)
                new_gate_spec.append("sg")
                new_gate_pos.append([g_pos[0]])
                new_gate_spec.append("sg")
                new_gate_pos.append([g_pos[1]])
                new_gate_spec.append("syc")
                new_gate_pos.append(g_pos)
                q_last_gate_list[g_pos[0]] = "syc"
                q_last_gate_list[g_pos[1]] = "syc"
            elif g == " swap" or g == "swap" or g == "SWAP":
                for _ in range(3):
                    new_gate_spec.append("syc")
                    new_gate_pos.append(g_pos)
                    new_gate_spec.append("sg")
                    new_gate_pos.append([g_pos[0]])
                    new_gate_spec.append("sg")
                    new_gate_pos.append([g_pos[1]])
                q_last_gate_list[g_pos[0]] = "sg"
                q_last_gate_list[g_pos[1]] = "sg"
            else:   # measurement and v in qcnn
                name = str(g).strip()
                # print(name)
                index = int(name[1:])
                if index not in measurement_pair:
                    measurement_pair[index] = [0,0]
                if name[0] == "v":
                    measurement_pair[index][1] = len(new_gate_spec)
                    new_gate_spec.append("v"+str(index))
                    new_gate_pos.append([g_pos[0]])
                    q_last_gate_list[g_pos[0]] = "v"
                elif name[0] == "m":
                    measurement_pair[index][0] = len(new_gate_spec)
                    new_gate_spec.append("m"+str(index))
                    new_gate_pos.append([g_pos[0]])
                    q_last_gate_list[g_pos[0]] = "m"
                else:
                    raise ValueError("invalid gate name\n")
    assert(len(new_gate_spec) == len(new_gate_pos))
    data["gate_spec"] = new_gate_spec
    data["gates"] = new_gate_pos
    # print("measurement_pair")
    # print(measurement_pair)
    return measurement_pair

def create_list_from_data(data):
    data_list = []  # create an empty list
    # append the items to the list in the same order.
    data_list.append(data.get('#e'))
    data_list.append(data.get('compiler'))
    data_list.append(data.get('fidelity_no_crosstalk'))
    data_list.append(data.get('fidelity'))
    data_list.append(data.get('g1'))
    data_list.append(data.get('g2'))
    data_list.append(data.get('D'))
    avg_idling_time = np.average(np.array(data.get('qubit_idling_time')))
    data_list.append(avg_idling_time)
    data_list.append(data.get('qubit_idling_time'))
    data_list.append(data.get('qubit_lifetime'))
    avg_two_quibt_gate_fid = np.average(np.array(data.get('two_qubit_gates_fidelity')))
    data_list.append(avg_two_quibt_gate_fid)
    data_list.append(data.get('two_qubit_gates_fidelity'))
    data_list.append(data.get('gates'))
    data_list.append(data.get('gate_spec'))
    return data_list


if __name__ == "__main__":
    # Initialize parser
    parser = argparse.ArgumentParser()
    # Adding optional argument
    parser.add_argument("csv_file", metavar='cf', type=str,
        help="csv_file to store gate and gate spec")
    parser.add_argument("device_set", metavar='DS', type=str,
        help="Device: hh: heavy-hexagonal (IBM), grid: sqaure")
    parser.add_argument("benchmark", metavar='B', type=str,
        help="Benchmark Set: arith or qaoa or qcnn")
    # Read arguments from command line
    args = parser.parse_args()
    
    if args.device_set == "hh":
        count_physical_qubit = 18
        fix_coupling = [[0,4], [1,2], [2,3], [3,4], [4,5], [5,6], [6,7], 
                    [2,8], [6,9], [10,11], [8,11], [11,12], [12,13], 
                    [13,14], [14,15], [15,16], [9,15], [13,17]]
    elif args.device_set == "grid":
        count_physical_qubit = 16
        fix_coupling = [[0,1], [1,2], [2,3], [4,5], [5,6], [6,7], [8,9],
        [9,10], [10,11], [12,13], [13,14], [14,15], [0,4], [4,8],
        [8,12], [1,5], [5,9], [9,13], [2,6], [6,10], [10,14],
        [3,7], [7,11], [11,15]]
    else:
        raise ValueError("invalid benchmark name\n")
    
    with open(args.csv_file, 'r') as r:
        print(args.csv_file)
        csvreader = csv.reader(r)
        header = []
        header = next(csvreader)
        data = dict()
        
        tmp = args.csv_file.split('/')
        csv_name = ""
        for i in range(len(tmp)-1):
            csv_name += (tmp[i] + '/')
        csv_name = csv_name + "sim/" + tmp[-1][:-4]+"_sim.csv"
        with open(csv_name, 'w+') as c:
            writer = csv.writer(c)
            writer.writerow([ '#e', 'compiler', 'fidelity no crosstalk', 'fidelity', 'g1', 'g2', 'D', 'avg idling time', 'idling time', 'qubit lifetime', 'avg two qubit gate fidelity', 'two qubit gate fidelity', 'gates', 'gate_spec'])


        if args.benchmark == "qcnn":
            measure_at_end = False
        else:
            measure_at_end = True

        # print(header)
        for row in csvreader:
            # print(row)
            data['compiler'] = row[0]
            data["gates"] = ast.literal_eval(row[3])
            data["gate_spec"] = ast.literal_eval(row[4])
            data["#e"] = ast.literal_eval(row[1])
            # print(data)
            coupling = ast.literal_eval(row[5]) + fix_coupling
            sim_circuit(count_physical_qubit, data, coupling, measure_at_end)
            with open(csv_name, 'a') as c:
                writer = csv.writer(c)
                data_list = create_list_from_data(data)
                writer.writerow(data_list)

    
    

    