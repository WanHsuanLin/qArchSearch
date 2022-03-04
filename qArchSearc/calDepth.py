import os
import argparse
import json
import csv
import pandas as pd
import numpy as np

from device import getNeighboringQubit
from util import get_list_of_json_files


def calDepth(data:dict):
    depth = 0
    contiU = 0
    for time_slot in data["gate_spec"]:
        if "u4" in time_slot:
            contiU += 1
        else:
            depth += contiU * 6 + 1 + 3  # 3 for swap gate
            contiU = 0
    depth += contiU * 6 + 1
    data["D"] = depth

def calExactDepth(data:dict):
    d = [0] * 16
    cg = ["SWAP"] * 16
    g1 = 0
    exact_gate_time = []
    gate_duration = []
    time_slot = 0
    for gate_pos, gate_type in zip(data["gates"],data["gate_spec"]):
        exact_gate_time.append([])
        gate_duration.append([])
        for pos, gtype in zip(gate_pos, gate_type):
            if gtype == "SWAP" or gtype == " swap":
                d[pos[0]] = max(d[pos[0]],d[pos[1]])+3
                gate_duration[time_slot].append(3)
            elif gtype == "u4" or gtype == " U4" or gtype == " U4 swap" :
                if cg[pos[0]] == cg[pos[1]]:
                    if cg[pos[0]] == "SWAP" or gtype == " swap":
                        d[pos[0]] = max(d[pos[0]],d[pos[1]])+7
                        g1 += 7
                        gate_duration[time_slot].append(7)
                    elif cg[pos[0]] == "u4" or gtype == " U4"  or gtype == " U4 swap" :
                        d[pos[0]] = max(d[pos[0]],d[pos[1]])+6
                        g1 += 5
                        gate_duration[time_slot].append(6)
                    else:
                        assert(False)
                elif (cg[pos[0]] == "SWAP" or gtype == " swap") and (cg[pos[1]] == "u4" or gtype == " U4"  or gtype == " U4 swap"):
                    d[pos[0]] = max(d[pos[0]]+7,d[pos[1]]+6)
                    g1 += 6
                    gate_duration[time_slot].append(7)
                elif (cg[pos[0]] == "u4" or gtype == " U4"  or gtype == " U4 swap") and (cg[pos[1]] == "SWAP" or gtype == " swap"):
                    d[pos[0]] = max(d[pos[0]]+6,d[pos[1]]+7)
                    g1 += 6
                    gate_duration[time_slot].append(7)
                else:
                    print(gtype)
                    assert (False)    
            else:
                print(gtype)
                assert (False)
            d[pos[1]] = d[pos[0]]
            exact_gate_time[time_slot].append(d[pos[0]])
            if gtype == "u4" or gtype == " U4" or gtype == " U4 swap":
                cg[pos[0]] = "u4"
                cg[pos[1]] = "u4"
            elif gtype == "SWAP" or gtype == " swap":
                cg[pos[0]] = "SWAP"
                cg[pos[1]] = "SWAP"
        time_slot += 1
    data["D"] = max(d)
    data["g1"] = g1
    data["exact_gate_time"] = exact_gate_time
    data["gate_duration"] = gate_duration


def checkCnot(cnot_matrix, possibleCrosstalkList, g, t):
    ori_crosstalk = 0
    for gc in cnot_matrix[t]:
        if gc in possibleCrosstalkList[g]:
            ori_crosstalk += 1
    return ori_crosstalk

def checkCrosstalk2g(g1_pos, g2_pos, dict_qubit_neighboringQubit):
    if g1_pos[0] in dict_qubit_neighboringQubit[g2_pos[0]] or (g1_pos[0] in dict_qubit_neighboringQubit[g2_pos[1]]) or (g1_pos[1] in dict_qubit_neighboringQubit[g2_pos[0]]) or (g1_pos[1] in dict_qubit_neighboringQubit[g2_pos[1]]):
                                return True
    else:
        return False


def checkCriticalPath(g, depth, flat_gate_duration, flat_exact_gate_time, counted_gate, cnot_matrix, front_gate):
    if depth == 0:
        return
    # print("check ", g);
    # print(front_gate[g])
    # print("depth ", depth)
    # print("flat_exact_gate_time ", flat_exact_gate_time[g])
    print(flat_exact_gate_time[g] == depth)
    if flat_exact_gate_time[g] == depth and g not in counted_gate: # it is on the critical path
        # print(g, " is on critical path")
        if flat_gate_duration[g] == 3:
            cnot_matrix[depth].append(g)
            cnot_matrix[depth-1].append(g)
            cnot_matrix[depth-2].append(g)
        elif flat_gate_duration[g] == 6 or flat_gate_duration[g] == 7 :
            cnot_matrix[depth-1].append(g)
            cnot_matrix[depth-3].append(g)
            cnot_matrix[depth-5].append(g)
        else:
            assert(False)
        counted_gate.add(g)
        depth -= flat_gate_duration[g]
        for pre_g in front_gate[g]:
            checkCriticalPath(pre_g, depth, flat_gate_duration, flat_exact_gate_time, counted_gate, cnot_matrix, front_gate)
        

def getPossibleCrosstalkList(flat_gates, dict_qubit_neighboringQubit):
    crosstalkList = [set()] * len(flat_gates)
    for i in len(flat_gates):
        for j in len(flat_gates):
            if checkCrosstalk2g(flat_gates[i], flat_gates[j], dict_qubit_neighboringQubit):
                crossstalkList[i].append(j)
                crossstalkList[j].append(i)
    return crossstalkList


def calg1(data:dict):
    g1 = 0
    for gate_pos in data["gates"]:
        for pos in gate_pos:
            if len(pos) == 1:
                g1 += 1
    data["g1"] = g1


def calculateCrosstalk(data:dict):
    device = data["device"]
    gate_pos = data["gates"]
    gate_spec = data["gate_spec"]
    # construct dict: qubit->list of neighboring qubit
    dict_qubit_neighboringQubit = getNeighboringQubit(device)
    
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
                        if checkCrosstalk2g(time_slot[j], time_slot[i], dict_qubit_neighboringQubit):
                            # num_crosstalk += 2
                            crosstalk_g.add(t * 100 + j)
                            # print("g",t * 100 + i, gate_names[i], time_slot[i]," and g", t * 100 + j, gate_names[j], time_slot[j], "have crosstalk effects")
                            i_crosstalk = True
                if i_crosstalk == True:
                    crosstalk_g.add(t * 100 + i)
        t += 1
    # print("number of crosstalk is ", (len(crosstalk_g)*3))
    # x = input()
    if args.benchmark == "qcnn" or args.benchmark == "qaoa" or "qv":
        return len(crosstalk_g)*3
    return len(crosstalk_g)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    # Adding optional argument
    parser.add_argument("folder", metavar='folder', type=str,
        help="Result Folder: each benchmark result")
    parser.add_argument("--g1", dest="ifg1", action='store_true',
        help="if you want to draw curve sorted by the index of device")
    args = parser.parse_args()
    list_of_files = get_list_of_json_files(args.folder)
    for file in list_of_files:
        # print(file)
        with open(file) as f:
            data = json.load(f)
        # calDepth(data)
        if args.ifg1:
            calg1(data)
            calExactDepth(data)
        else:
            # calExactDepth(data)
            # calCrosstalk(data)
            pushToRight(data)
        
        with open(file, 'w+') as f:
            json.dump(data, f)


