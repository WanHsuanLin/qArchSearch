import os
import numpy as np
from qArchSearch.olsq.device import qcDeviceSet
from qArchSearch.device import getNeighboringQubit

SINGLE_QUBIT_GATE_FID = 0.999
TWO_QUBIT_GATE_FID = 0.99
CT_TWO_QUBIT_GATE_FID = 0.985
COHERENCE_TIME = 1000

def get_list_of_json_files(folder):
    # list_of_files = os.listdir(args.folder)
    list_of_files = []
    for root, pathnames, files in os.walk(folder):
        for f in files:
            fullpath = os.path.join(root, f)
            list_of_files.append(fullpath)
    return list_of_files

def get_qaoa_graph(size:int, trial:int):
    qaoa = {
        "16": [[(4, 15), (4, 11), (4, 10), (15, 10), (15, 7), (0, 5), (0, 13), (0, 12), (5, 9), (5, 1), (2, 11), (2, 7), (2, 12), (11, 1), (1, 9), (9, 7), (10, 8), (13, 14), (13, 6), (14, 6), (14, 8), (6, 3), (3, 12), (3, 8)],
    [(3, 4), (3, 9), (3, 8), (4, 14), (4, 7), (5, 13), (5, 9), (5, 1), (13, 6), (13, 1), (8, 12), (8, 11), (12, 15), (12, 11), (2, 11), (2, 10), (2, 15), (10, 15), (10, 0), (6, 14), (6, 0), (14, 7), (9, 7), (0, 1)],
    [(4, 12), (4, 11), (4, 10), (12, 8), (12, 0), (5, 7), (5, 13), (5, 6), (7, 2), (7, 1), (13, 3), (13, 14), (3, 1), (3, 8), (0, 2), (0, 1), (2, 6), (8, 15), (9, 11), (9, 15), (9, 6), (11, 10), (15, 14), (14, 10)],
    [(4, 12), (4, 11), (4, 0), (12, 13), (12, 15), (3, 10), (3, 11), (3, 0), (10, 14), (10, 1), (5, 7), (5, 2), (5, 9), (7, 9), (7, 6), (13, 0), (13, 8), (9, 14), (14, 15), (2, 11), (2, 6), (1, 15), (1, 8), (6, 8)],
    [(6, 12), (6, 15), (6, 13), (12, 14), (12, 9), (15, 14), (15, 7), (5, 10), (5, 0), (5, 9), (10, 11), (10, 4), (0, 13), (0, 3), (9, 2), (4, 11), (4, 7), (11, 8), (14, 7), (8, 1), (8, 3), (1, 2), (1, 13), (2, 3)],
    [(3, 7), (3, 9), (3, 11), (7, 9), (7, 11), (4, 12), (4, 15), (4, 14), (12, 10), (12, 1), (15, 0), (15, 11), (0, 2), (0, 14), (2, 8), (2, 1), (5, 10), (5, 1), (5, 8), (10, 6), (14, 13), (8, 6), (13, 9), (13, 6)],
    [(6, 12), (6, 1), (6, 9), (12, 4), (12, 5), (3, 4), (3, 9), (3, 5), (4, 0), (1, 15), (1, 8), (8, 15), (8, 14), (15, 13), (2, 11), (2, 7), (2, 13), (11, 10), (11, 5), (7, 13), (7, 14), (9, 0), (14, 10), (10, 0)],
    [(3, 4), (3, 7), (3, 0), (4, 0), (4, 1), (7, 8), (7, 14), (2, 5), (2, 9), (2, 15), (5, 6), (5, 14), (1, 12), (1, 15), (12, 9), (12, 11), (15, 14), (6, 10), (6, 0), (10, 11), (10, 8), (11, 13), (9, 13), (13, 8)],
    [(4, 12), (4, 15), (4, 13), (12, 1), (12, 2), (3, 10), (3, 11), (3, 8), (10, 7), (10, 1), (15, 5), (15, 2), (0, 5), (0, 1), (0, 6), (5, 8), (11, 14), (11, 7), (14, 6), (14, 8), (7, 13), (6, 9), (13, 9), (9, 2)],
    [(6, 12), (6, 3), (6, 0), (12, 4), (12, 11), (4, 9), (4, 0), (9, 14), (9, 5), (5, 10), (5, 1), (10, 14), (10, 13), (14, 2), (0, 8), (8, 2), (8, 11), (1, 3), (1, 15), (3, 11), (2, 7), (15, 7), (15, 13), (7, 13)]],

    "8": [[(0, 1), (0, 4), (0, 3), (1, 7), (1, 6), (2, 4), (2, 7), (2, 3), (4, 6), (7, 5), (6, 5), (3, 5)],
    [(0, 7), (0, 3), (0, 2), (7, 3), (7, 4), (1, 2), (1, 5), (1, 6), (2, 5), (3, 4), (4, 6), (5, 6)],
    [(4, 6), (4, 1), (4, 7), (6, 0), (6, 5), (0, 3), (0, 2), (3, 2), (3, 1), (1, 7), (5, 7), (5, 2)],
    [(0, 1), (0, 3), (0, 6), (1, 7), (1, 6), (2, 4), (2, 7), (2, 5), (4, 3), (4, 5), (3, 6), (7, 5)],
    [(0, 7), (0, 6), (0, 2), (7, 1), (7, 4), (2, 4), (2, 6), (4, 3), (3, 1), (3, 5), (1, 5), (5, 6)],
    [(0, 1), (0, 4), (0, 6), (1, 5), (1, 3), (4, 6), (4, 5), (2, 7), (2, 3), (2, 5), (7, 3), (7, 6)],
    [(0, 1), (0, 4), (0, 3), (1, 2), (1, 5), (2, 7), (2, 6), (4, 6), (4, 7), (7, 5), (5, 3), (3, 6)],
    [(0, 1), (0, 7), (0, 2), (1, 5), (1, 6), (7, 2), (7, 4), (2, 4), (4, 3), (3, 6), (3, 5), (5, 6)],
    [(2, 4), (2, 7), (2, 5), (4, 1), (4, 7), (7, 6), (1, 5), (1, 3), (5, 0), (0, 3), (0, 6), (3, 6)],
    [(2, 4), (2, 0), (2, 5), (4, 3), (4, 1), (3, 0), (3, 1), (0, 6), (5, 7), (5, 6), (7, 6), (7, 1)]],

    "10": [[(0, 1), (0, 3), (0, 8), (1, 2), (1, 5), (3, 8), (3, 5), (8, 9), (2, 7), (2, 6), (7, 5), (7, 4), (4, 9), (4, 6), (9, 6)],
    [(5, 8), (5, 4), (5, 2), (8, 7), (8, 2), (4, 9), (4, 6), (9, 0), (9, 7), (0, 3), (0, 2), (3, 6), (3, 1), (6, 1), (7, 1)],
    [(0, 7), (0, 2), (0, 8), (7, 6), (7, 1), (3, 8), (3, 4), (3, 5), (8, 6), (1, 2), (1, 9), (2, 5), (4, 9), (4, 5), (9, 6)],
    [(0, 1), (0, 4), (0, 5), (1, 6), (1, 9), (2, 4), (2, 6), (2, 5), (4, 8), (3, 7), (3, 6), (3, 5), (7, 9), (7, 8), (9, 8)],
    [(0, 1), (0, 4), (0, 5), (1, 6), (1, 9), (3, 8), (3, 7), (3, 2), (8, 9), (8, 2), (4, 9), (4, 5), (2, 7), (7, 6), (6, 5)],
    [(0, 1), (0, 7), (0, 4), (1, 5), (1, 9), (7, 9), (7, 6), (3, 8), (3, 4), (3, 5), (8, 6), (8, 2), (4, 9), (5, 2), (6, 2)],
    [(0, 1), (0, 4), (0, 6), (1, 2), (1, 8), (3, 8), (3, 7), (3, 5), (8, 2), (2, 4), (4, 6), (7, 5), (7, 9), (6, 9), (5, 9)],
    [(0, 1), (0, 2), (0, 8), (1, 3), (1, 9), (4, 6), (4, 7), (4, 8), (6, 2), (6, 5), (5, 7), (5, 3), (7, 8), (2, 9), (9, 3)],
    [(0, 1), (0, 3), (0, 8), (1, 5), (1, 6), (3, 8), (3, 7), (8, 7), (2, 4), (2, 9), (2, 6), (4, 9), (4, 7), (5, 9), (5, 6)],
    [(0, 1), (0, 6), (0, 8), (1, 4), (1, 9), (2, 4), (2, 9), (2, 6), (4, 6), (5, 8), (5, 7), (5, 3), (8, 7), (3, 7), (3, 9)]],

    "12": [[(0, 1), (0, 3), (0, 11), (1, 5), (1, 9), (4, 10), (4, 2), (4, 5), (10, 7), (10, 6), (2, 9), (2, 11), (3, 8), (3, 6), (8, 7), (8, 11), (5, 7), (6, 9)],
    [(9, 10), (9, 4), (9, 11), (10, 3), (10, 5), (0, 1), (0, 2), (0, 5), (1, 2), (1, 6), (2, 8), (6, 11), (6, 3), (11, 7), (4, 5), (4, 8), (3, 7), (7, 8)],
    [(0, 1), (0, 10), (0, 8), (1, 7), (1, 10), (2, 4), (2, 9), (2, 11), (4, 9), (4, 8), (10, 5), (6, 11), (6, 5), (6, 3), (11, 8), (9, 7), (3, 7), (3, 5)],
    [(0, 10), (0, 3), (0, 11), (10, 2), (10, 8), (6, 11), (6, 5), (6, 1), (11, 2), (4, 9), (4, 5), (4, 8), (9, 1), (9, 7), (3, 7), (3, 1), (7, 5), (2, 8)],
    [(9, 10), (9, 8), (9, 1), (10, 0), (10, 6), (0, 7), (0, 6), (7, 3), (7, 4), (2, 4), (2, 1), (2, 5), (4, 5), (1, 3), (5, 11), (11, 8), (11, 3), (6, 8)],
    [(0, 1), (0, 10), (0, 3), (1, 4), (1, 6), (2, 4), (2, 8), (2, 10), (4, 6), (5, 11), (5, 8), (5, 9), (11, 9), (11, 3), (10, 7), (8, 9), (3, 7), (7, 6)],
    [(0, 1), (0, 10), (0, 6), (1, 11), (1, 9), (9, 10), (9, 11), (10, 7), (2, 8), (2, 3), (2, 5), (8, 5), (8, 4), (5, 3), (11, 3), (7, 4), (7, 6), (4, 6)],
    [(9, 10), (9, 5), (9, 1), (10, 8), (10, 5), (0, 7), (0, 6), (0, 5), (7, 3), (7, 1), (3, 8), (3, 4), (8, 2), (2, 4), (2, 11), (4, 11), (6, 11), (6, 1)],
    [(9, 10), (9, 0), (9, 8), (10, 7), (10, 3), (2, 4), (2, 6), (2, 5), (4, 1), (4, 5), (1, 11), (1, 6), (11, 7), (11, 3), (7, 8), (0, 6), (0, 8), (3, 5)],
    [(0, 1), (0, 10), (0, 6), (1, 8), (1, 7), (2, 4), (2, 9), (2, 11), (4, 9), (4, 11), (5, 11), (5, 8), (5, 3), (10, 3), (10, 6), (8, 7), (9, 6), (3, 7)]],

    "14": [[(3, 13), (3, 6), (3, 0), (13, 9), (13, 6), (5, 10), (5, 0), (5, 4), (10, 11), (10, 1), (0, 7), (1, 6), (1, 4), (9, 11), (9, 12), (11, 12), (2, 8), (2, 7), (2, 12), (8, 4), (8, 7)],
    [(6, 12), (6, 0), (6, 9), (12, 8), (12, 5), (4, 9), (4, 5), (4, 13), (9, 1), (0, 2), (0, 5), (2, 7), (2, 13), (8, 3), (8, 10), (1, 3), (1, 13), (3, 11), (7, 10), (7, 11), (10, 11)],
    [(4, 12), (4, 7), (4, 10), (12, 5), (12, 9), (5, 13), (5, 8), (13, 3), (13, 10), (3, 1), (3, 11), (0, 2), (0, 7), (0, 6), (2, 10), (2, 9), (8, 9), (8, 11), (1, 6), (1, 7), (6, 11)],
    [(3, 13), (3, 8), (3, 0), (13, 7), (13, 6), (0, 5), (0, 8), (5, 6), (5, 1), (8, 11), (10, 12), (10, 7), (10, 4), (12, 9), (12, 2), (1, 9), (1, 2), (9, 2), (6, 11), (11, 4), (7, 4)],
    [(4, 6), (4, 2), (4, 1), (6, 5), (6, 10), (12, 13), (12, 3), (12, 7), (13, 7), (13, 11), (5, 7), (5, 8), (0, 2), (0, 11), (0, 9), (2, 8), (8, 9), (9, 3), (1, 3), (1, 10), (11, 10)],
    [(6, 12), (6, 8), (6, 2), (12, 5), (12, 11), (3, 7), (3, 1), (3, 8), (7, 13), (7, 4), (1, 9), (1, 11), (9, 5), (9, 10), (8, 11), (13, 0), (13, 2), (4, 5), (4, 0), (10, 0), (10, 2)],
    [(6, 12), (6, 4), (6, 7), (12, 0), (12, 11), (3, 7), (3, 13), (3, 9), (7, 0), (4, 5), (4, 8), (5, 13), (5, 2), (13, 2), (8, 9), (8, 2), (9, 1), (1, 11), (1, 10), (0, 10), (10, 11)],
    [(4, 6), (4, 5), (4, 8), (6, 1), (6, 11), (5, 13), (5, 0), (13, 8), (13, 1), (0, 1), (0, 3), (11, 10), (11, 3), (7, 10), (7, 12), (7, 8), (10, 2), (3, 9), (9, 12), (9, 2), (2, 12)],
    [(12, 13), (12, 10), (12, 0), (13, 9), (13, 11), (3, 10), (3, 1), (3, 8), (10, 6), (0, 2), (0, 5), (2, 11), (2, 4), (8, 9), (8, 1), (9, 5), (5, 4), (1, 6), (6, 7), (11, 7), (4, 7)],
    [(4, 12), (4, 8), (4, 1), (12, 1), (12, 9), (0, 2), (0, 10), (0, 13), (2, 5), (2, 10), (9, 11), (9, 5), (11, 3), (11, 5), (1, 7), (7, 13), (7, 8), (13, 6), (8, 3), (3, 6), (6, 10)]],
    
    "4": [[(0, 1), (0, 3), (0, 2), (1, 2), (1, 3), (2, 3)]],

    "6": [[(0, 1), (0, 4), (0, 5), (1, 2), (1, 4), (2, 3), (2, 5), (4, 3), (3, 5)]]

    }

    return qaoa[str(size)][trial]

def is_crosstalk(g1_pos, g2_pos, dict_qubit_neighboringQubit):
    if g1_pos[0] in dict_qubit_neighboringQubit[g2_pos[0]] or (g1_pos[0] in dict_qubit_neighboringQubit[g2_pos[1]]) or (g1_pos[1] in dict_qubit_neighboringQubit[g2_pos[0]]) or (g1_pos[1] in dict_qubit_neighboringQubit[g2_pos[1]]):
                                return True
    else:
        return False

def cal_crosstalk(data:dict, b, coupling, device_qubit):
    gate_pos = data["gates"]
    gate_spec = data["gate_spec"]
    # construct dict: qubit->list of neighboring qubit
    dict_qubit_neighboringQubit = getNeighboringQubit(coupling, device_qubit)
    
    # calculate the number of gates effected by crosstalk
    num_crosstalk = 0
    crosstalk_g = set()
    # print("Device: ", device)
    # print("Gate pos: ", gate_pos)
    # print("Gate name: ", gate_spec)
    t = 0
    for time_slot, gate_names in zip(gate_pos, gate_spec):
        # multiple gates on the same time slot
        if len(time_slot) > 1:
            for i in range(len(time_slot)):
                i_crosstalk = False
                if len(time_slot[i]) > 1:
                    for j in range(i+1,len(time_slot)):
                        # if the endpoint of the gate[j] is the neighbor of the endpoint of gate[i], crosstalk occurs.
                        # if gate_names[i] == gate_names[j]:
                            # if (time_slot[j][0] in dict_qubit_neighboringQubit[time_slot[i][0]]) or (time_slot[j][0] in dict_qubit_neighboringQubit[time_slot[i][1]]) \
                            #     or (time_slot[j][1] in dict_qubit_neighboringQubit[time_slot[i][0]]) or (time_slot[j][1] in dict_qubit_neighboringQubit[time_slot[i][1]]):
                        if is_crosstalk(time_slot[j], time_slot[i], dict_qubit_neighboringQubit):
                            # num_crosstalk += 2
                            crosstalk_g.add(t * 100 + j)
                            # print("g",t * 100 + i, gate_names[i], time_slot[i]," and g", t * 100 + j, gate_names[j], time_slot[j], "have crosstalk effects")
                            i_crosstalk = True
                if i_crosstalk == True:
                    crosstalk_g.add(t * 100 + i)
        t += 1
    # print("number of crosstalk is ", (len(crosstalk_g)*3))
    # x = input()
    if b == "qcnn" or b == "qaoa" or "qv":
        return len(crosstalk_g)*3
    return len(crosstalk_g)

def cal_fidelity(info):
    fidelity = pow(SINGLE_QUBIT_GATE_FID, info['g1']) * pow(TWO_QUBIT_GATE_FID, info['g2']) * np.exp(-(info['M'] * info['D'] - 2 * info['g2'] - info['g1'])/COHERENCE_TIME)
    fidelity_ct = pow(SINGLE_QUBIT_GATE_FID, info['g1']) * pow(TWO_QUBIT_GATE_FID, (info['g2']-info['crosstalk'])) * pow(CT_TWO_QUBIT_GATE_FID, info['crosstalk']) * np.exp(-(info['M'] * info['D'] - 2 * info['g2'] - info['g1'])/COHERENCE_TIME)
    return fidelity, fidelity_ct

def cal_cost_scaled_fidelity(info):
    cft = info['fidelity'] / info['cost']
    cft_ct = info['fidelity_ct'] / info['cost']
    return cft, cft_ct

def cal_cost(num_extra_connection: int):
    cost = 56 + num_extra_connection  # 2×16+24
    return cost

def cal_QCNN_depth_g2_g1(gates:list,gate_spec:list,num_qubit:int):
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

def cal_QAOA_depth(gates:list,gate_spec:list,num_qubit:int):
    d = [0] * num_qubit
    cg = ["swap"] * num_qubit
    for gate_pos, gate_type in zip(gates,gate_spec):
        for pos, gtype in zip(gate_pos, gate_type):
            # print(pos)
            gtype = gtype.lstrip().lstrip()
            # print(gtype)
            
            if gtype == "swap" or gtype == "ZZ" or gtype == "ZZ ZZ":
                d[pos[0]] = max(d[pos[0]],d[pos[1]])+3
            # elif gtype == "ZZ swap" or "swap ZZ":
            else:
                d[pos[0]] = max(d[pos[0]],d[pos[1]])+4
            # else:
            #     assert(False)
            d[pos[1]] = d[pos[0]]
            cg[pos[0]] = gtype
            cg[pos[1]] = gtype
    return max(d)