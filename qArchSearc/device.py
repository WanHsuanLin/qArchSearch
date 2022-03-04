import os
import sys
import argparse
import json
dir_path = os.getcwd()
sys.path.append(dir_path)
from olsq.device import qcdevice


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

def get_deviceND(device: int, benchmark:str, fidelity):
    # basic couplings, i.e., edges, of a 4*4 grid, i.e., device0
    # my_coupling = [(0,1), (1,2), (2,3), (3,4), (4,5), (5,6), (6,7),
    #     (0,8), (1,9), (2,10), (3,11), (4,12), (5,13), (6,14), (7,15),
    #     (8,9), (9,10), (10,11), (11,12), (12,13), (13,14), (14,15)]

    my_coupling = [(0,1), (1,2), (2,3), (4,5), (5,6), (6,7), (8,9),
        (9,10), (10,11), (12,13), (13,14), (14,15), (0,4), (4,8),
        (8,12), (1,5), (5,9), (9,13), (2,6), (6,10), (10,14),
        (3,7), (7,11), (11,15)]
    # 6 circuit for only one connection
    if device == 0:
        my_coupling += [(0,5)]
    elif device == 1:
        my_coupling += [(1,4)]
    elif device == 2:
        my_coupling += [(1,6)]
    elif device == 3:
        my_coupling += [(2,5)]
    elif device == 4:
        my_coupling += [(5,10)]
    elif device == 5:
        my_coupling += [(6,9)]
    elif device == 6:
        my_coupling += [(0,5),(1,6)]
    elif device == 7:
        my_coupling += [(0,5),(5,10)]
    elif device == 8:
        my_coupling += [(0,5),(2,7)]
    elif device == 9:
        my_coupling += [(0,5),(6,11)]
    elif device == 10:
        my_coupling += [(0,5),(10,15)]
    elif device == 11:
        my_coupling += [(1,4),(2,5)]
    elif device == 12:
        my_coupling += [(1,4),(6,9)]
    elif device == 13:
        my_coupling += [(1,4),(7,10)]
    elif device == 14:
        my_coupling += [(1,4),(11,14)]
    elif device == 15:
        my_coupling += [(5,8),(6,9)]
    elif device == 16:
        my_coupling += [(2,5),(6,9)]
    elif device == 17:
        my_coupling += [(0,5),(9,12)]
    elif device == 18:
        my_coupling += [(4,9),(9,12)]
    elif device == 19:
        my_coupling += [(1,6),(9,12)]
    elif device == 20:
        my_coupling += [(5,10),(9,12)]
    elif device == 21:
        my_coupling += [(2,7),(9,12)]
    elif device == 22:
        my_coupling += [(5,8),(2,7)]
    elif device == 23:
        my_coupling += [(2,5),(2,7)]
    elif device == 24:
        my_coupling += [(6,9),(2,7)]
    elif device == 25:
        my_coupling += [(11,14),(2,7)]
    elif device == 26:
        my_coupling += [(1,6),(4,9)]
    elif device == 27:
        my_coupling += [(1,6),(9,14)]
    elif device == 28:
        my_coupling += [(1,6),(6,11)]
    elif device == 29:
        my_coupling += [(1,6),(5,8)]
    elif device == 30:
        my_coupling += [(1,6),(10,13)]
    elif device == 31:
        my_coupling += [(0,5),(1,4)]
    elif device == 32:
        my_coupling += [(1,6),(2,5)]
    elif device == 33:
        my_coupling += [(5,10),(6,9)]
    else:
        assert (device == -1)
    

    # qaoa and qcnn: swap_duration=1 since SWAP is comparable to the gates
    # for arith, use 3
    my_swap_duration = 1
    if benchmark == "arith":
        my_swap_duration = 3

    if fidelity:
        my_ftwo = [0.99]*len(my_coupling)
        return qcdevice(name=str(device), nqubits=16,
            connection=my_coupling, swap_duration=my_swap_duration, ftwo = my_ftwo)
    else:
        return qcdevice(name=str(device), nqubits=16,
            connection=my_coupling, swap_duration=my_swap_duration)

def get_device(device: int, benchmark:str, fidelity):
    # basic couplings, i.e., edges, of a 4*4 grid, i.e., device0
    # my_coupling = [(0,1), (1,2), (2,3), (3,4), (4,5), (5,6), (6,7),
    #     (0,8), (1,9), (2,10), (3,11), (4,12), (5,13), (6,14), (7,15),
    #     (8,9), (9,10), (10,11), (11,12), (12,13), (13,14), (14,15)]

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

    # qaoa and qcnn: swap_duration=1 since SWAP is comparable to the gates
    # for arith, use 3
    my_swap_duration = 1
    if benchmark == "arith":
        my_swap_duration = 3


    if fidelity:
        my_ftwo = [0.99]*len(my_coupling)
        return qcdevice(name=str(device), nqubits=16,
            connection=my_coupling, swap_duration=my_swap_duration, ftwo = my_ftwo)
    else:
        return qcdevice(name=str(device), nqubits=16,
            connection=my_coupling, swap_duration=my_swap_duration)

def get_coupling(device: int):
    # basic couplings, i.e., edges, of a 4*4 grid, i.e., device0
    # my_coupling = [(0,1), (1,2), (2,3), (3,4), (4,5), (5,6), (6,7),
    #     (0,8), (1,9), (2,10), (3,11), (4,12), (5,13), (6,14), (7,15),
    #     (8,9), (9,10), (10,11), (11,12), (12,13), (13,14), (14,15)]

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

def getNeighboringQubit(device):
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
    tmp = device
    edge_list = []
    if tmp % 2 == 1:
        edge_list += [(0,5), (3,6), (9,12), (10,15)]
    tmp = tmp // 2
    if tmp % 2 == 1:
        edge_list += [(1,4), (2,7), (8,13), (11,14)]
    tmp = tmp // 2
    if tmp % 2 == 1:
        edge_list += [(1,6), (10, 13)]
    tmp = tmp // 2
    if tmp % 2 == 1:
        edge_list += [(2,5), (9,14)]
    tmp = tmp // 2
    if tmp % 2 == 1:
        edge_list += [(4,9), (7,10)]
    tmp = tmp // 2
    if tmp % 2 == 1:
        edge_list += [(5,8), (6,11)]
    tmp = tmp // 2
    if tmp % 2 == 1:
        edge_list += [(5,10)]
    tmp = tmp // 2
    if tmp % 2 == 1:
        edge_list += [(6,9)]

    for edge in edge_list:
            dict_qubit_neighboringQubit[edge[0]].append(edge[1])
            dict_qubit_neighboringQubit[edge[1]].append(edge[0])
    return dict_qubit_neighboringQubit
