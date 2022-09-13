from qArchSearch.device import qcDeviceSet


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

def get_device_set_square_4by4():
    # basic couplings, i.e., edges, of a 4*4 grid, i.e., device0
    basic_coupling = [(0,1), (1,2), (2,3), (4,5), (5,6), (6,7), (8,9),
        (9,10), (10,11), (12,13), (13,14), (14,15), (0,4), (4,8),
        (8,12), (1,5), (5,9), (9,13), (2,6), (6,10), (10,14),
        (3,7), (7,11), (11,15)]
    extra_coupling = [(0,5), (3,6), (9,12), (10,15), (1,4), (2,7), (8,13), (11,14),
        (1,6), (10, 13), (2,5), (9,14), (4,9), (7,10), (5,8), (6,11),
        (5,10), (6,9)]
    conflict_coupling_set = [[(0,5), (1,4)],[(1,6), (2,5)], [(3,6), (2,7)], [(4,9), (5,8)], [(5,10), (6,9)], [(6,11), (7,10)], [(9,12), (8,13)], [(9,14), (10,13)], [(10,15), (11,14)], ]
    # for arith, use 3

    return qcDeviceSet(name="square_4by4", nqubits=16,
        connection=basic_coupling, extra_connection = extra_coupling, conflict_coupling_set=conflict_coupling_set)


def get_device_set_hh(benchmark:str):
    basic_coupling = [(0,4), (1,2), (2,3), (3,4), (4,5), (5,6), (6,7), (2,8), (6,9), (10,11), (8,11), (11,12), (12,13), (13,14), (14,15), (15,16), (9,15), (13,17)]
    extra_coupling = [(3,8), (8,12), (3,12), (3,13), (4,12), (4,13), (4,14), (5,13), (5,14), (5,15), (6,14),
                        (2,12), (3,11), (9,14), (5,9), (0,3), (0,5), (12,17), (14,17), (6,7), (9,16), (1,8), (8,10)]
    conflict_coupling_set = [[(3,13), (4,12)], [(4,14), (5,13)], [(5,15), (6,14)],
                                [(3,8), (2,12)], [(8,12), (3,11)], [(2,12), (3,11)], [(5,15), (9,14)], [(6,14), (5,9)], [(5,9), (9,14)]]
    
    return qcDeviceSet(name="hh", nqubits=18,
        connection=basic_coupling, extra_connection = extra_coupling, conflict_coupling_set=conflict_coupling_set)

def getNeighboringQubit(list_qubit_edge, qubit_number):
    # construct dict: qubit->list of neighboring qubit
    dict_qubit_neighboringQubit = {}
    for i in range(qubit_number):
        dict_qubit_neighboringQubit[i] = []

    for edge in list_qubit_edge:
            dict_qubit_neighboringQubit[edge[0]].append(edge[1])
            dict_qubit_neighboringQubit[edge[1]].append(edge[0])
    return dict_qubit_neighboringQubit