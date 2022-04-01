import os
import sys
import argparse
import json
from qArchSearch.olsq.device import qcDeviceSet


def get_char_graph(coupling:list):
    # draw a character graph of the coupling graph
    char_graph = list()
    char_graph.append("00--01--02--03")

    tmp = "| "
    if (( 0, 5)     in coupling) and (( 1, 4) not in coupling):
        tmp += "\\"
    if (( 0, 5) not in coupling) and (( 1, 4)     in coupling):
        tmp += "/"
    if (( 0, 5)     in coupling) and (( 1, 4)     in coupling):
        tmp += "X"
    if (( 0, 5) not in coupling) and (( 1, 4) not in coupling):
        tmp += " "
    tmp += " | "
    if (( 1, 6)     in coupling) and (( 2, 5) not in coupling):
        tmp += "\\"
    if (( 1, 6) not in coupling) and (( 2, 5)     in coupling):
        tmp += "/"
    if (( 1, 6)     in coupling) and (( 2, 5)     in coupling):
        tmp += "X"
    if (( 1, 6) not in coupling) and (( 2, 5) not in coupling):
        tmp += " "
    tmp += " | "
    if (( 2, 7)     in coupling) and (( 3, 6) not in coupling):
        tmp += "\\"
    if (( 2, 7) not in coupling) and (( 3, 6)     in coupling):
        tmp += "/"
    if (( 2, 7)     in coupling) and (( 3, 6)     in coupling):
        tmp += "X"
    if (( 2, 7) not in coupling) and (( 3, 6) not in coupling):
        tmp += " "
    tmp += " |"
    char_graph.append(tmp)
    
    char_graph.append("04--05--06--07")

    tmp = "| "
    if (( 4, 9)     in coupling) and (( 5, 8) not in coupling):
        tmp += "\\"
    if (( 4, 9) not in coupling) and (( 5, 8)     in coupling):
        tmp += "/"
    if (( 4, 9)     in coupling) and (( 5, 8)     in coupling):
        tmp += "X"
    if (( 4, 9) not in coupling) and (( 5, 8) not in coupling):
        tmp += " "
    tmp += " | "
    if (( 5,10)     in coupling) and (( 6, 9) not in coupling):
        tmp += "\\"
    if (( 5,10) not in coupling) and (( 6, 9)     in coupling):
        tmp += "/"
    if (( 5,10)     in coupling) and (( 6, 9)     in coupling):
        tmp += "X"
    if (( 5,10) not in coupling) and (( 6, 9) not in coupling):
        tmp += " "
    tmp += " | "
    if (( 6,11)     in coupling) and (( 7,10) not in coupling):
        tmp += "\\"
    if (( 6,11) not in coupling) and (( 7,10)     in coupling):
        tmp += "/"
    if (( 6,11)     in coupling) and (( 7,10)     in coupling):
        tmp += "X"
    if (( 6,11) not in coupling) and (( 7,10) not in coupling):
        tmp += " "
    tmp += " |"
    char_graph.append(tmp)

    char_graph.append("08--09--10--11")

    tmp = "| "
    if (( 8,13)     in coupling) and (( 9,12) not in coupling):
        tmp += "\\"
    if (( 8,13) not in coupling) and (( 9,12)     in coupling):
        tmp += "/"
    if (( 8,13)     in coupling) and (( 9,12)     in coupling):
        tmp += "X"
    if (( 8,13) not in coupling) and (( 9,12) not in coupling):
        tmp += " "
    tmp += " | "
    if (( 9,14)     in coupling) and ((10,13) not in coupling):
        tmp += "\\"
    if (( 9,14) not in coupling) and ((10,13)     in coupling):
        tmp += "/"
    if (( 9,14)     in coupling) and ((10,13)     in coupling):
        tmp += "X"
    if (( 9,14) not in coupling) and ((10,13) not in coupling):
        tmp += " "
    tmp += " | "
    if ((10,15)     in coupling) and ((11,14) not in coupling):
        tmp += "\\"
    if ((10,15) not in coupling) and ((11,14)     in coupling):
        tmp += "/"
    if ((10,15)     in coupling) and ((11,14)     in coupling):
        tmp += "X"
    if ((10,15) not in coupling) and ((11,14) not in coupling):
        tmp += " "
    tmp += " |"
    char_graph.append(tmp)

    
    char_graph.append("12--13--14--15")

    graph = ""
    for line in char_graph:
        graph += line + "\n"
    return graph

def get_device_set(benchmark:str):
    # basic couplings, i.e., edges, of a 4*4 grid, i.e., device0
    basic_coupling = [(0,1), (1,2), (2,3), (4,5), (5,6), (6,7), (8,9),
        (9,10), (10,11), (12,13), (13,14), (14,15), (0,4), (4,8),
        (8,12), (1,5), (5,9), (9,13), (2,6), (6,10), (10,14),
        (3,7), (7,11), (11,15)]
    extra_coupling = [(0,5), (3,6), (9,12), (10,15), (1,4), (2,7), (8,13), (11,14),
        (1,6), (10, 13), (2,5), (9,14), (4,9), (7,10), (5,8), (6,11),
        (5,10), (6,9)]
    # qaoa and qcnn: swap_duration=1 since SWAP is comparable to the gates
    # for arith, use 3
    my_swap_duration = 1
    if benchmark == "arith":
        my_swap_duration = 3

    return qcDeviceSet(name="4by4_full", nqubits=16,
        connection=basic_coupling, extra_connection = extra_coupling, swap_duration=my_swap_duration)

def get_coupling(device: int):
    # basic couplings, i.e., edges, of a 4*4 grid, i.e., device0
    my_coupling = [(0,1), (1,2), (2,3), (4,5), (5,6), (6,7), (8,9),
        (9,10), (10,11), (12,13), (13,14), (14,15), (0,4), (4,8),
        (8,12), (1,5), (5,9), (9,13), (2,6), (6,10), (10,14),
        (3,7), (7,11), (11,15),
        (0,5), (3,6), (9,12), (10,15), (1,4), (2,7), (8,13), (11,14),
        (1,6), (10, 13), (2,5), (9,14), (4,9), (7,10), (5,8), (6,11),
        (5,10), (6,9)]

    return my_coupling

def getNeighboringQubit(extra_edge_list):
    # construct dict: qubit->list of neighboring qubit
    dict_qubit_neighboringQubit = {0:[1,4],
                                    1:[0,2,5],
                                    2:[1,3,6],
                                    3:[2,7],
                                    4:[5,0,8],
                                    5:[4,6,1,9],
                                    6:[5,7,2,10],
                                    7:[6,3,11],
                                    8:[9,4,12],
                                    9:[8,10,5,13],
                                    10:[9,11,6,14],
                                    11:[10,7,15],
                                    12:[13,8],
                                    13:[12,14,9],
                                    14:[13,15,10],
                                    15:[14,11]}

    for edge in extra_edge_list:
            dict_qubit_neighboringQubit[edge[0]].append(edge[1])
            dict_qubit_neighboringQubit[edge[1]].append(edge[0])
    return dict_qubit_neighboringQubit
