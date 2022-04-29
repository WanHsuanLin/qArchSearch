
def get_best_coupling_hh(circuit_info):
    if isinstance(circuit_info, str): 
        coupling = [(0,4), (1,2), (2,3), (3,4), (4,5), (5,6), (6,7), 
                    (2,8), (6,9), (10,11), (8,11), (11,12), (12,13), 
                    (13,14), (14,15), (15,16), (9,15), (13,17)]
        if circuit_info == "qcnn/8-4-2.qasm":
            coupling += [(6, 14), (9, 14), (14, 17), (9, 16)]
        elif circuit_info == "qcnn/10-5-3-2.qasm":
            coupling += [(3, 8), (8, 12), (3, 12), (3, 13), (4, 13), (4, 14), (0, 3)]
        elif circuit_info == "qcnn/12-6-3-2.qasm":
            coupling += []
        else:
            raise ValueError("Invalid circuit")
    else:
        raise ValueError("Invalid circuit")
    return coupling

def get_best_coupling_grid(circuit_info):
    if isinstance(circuit_info, str): 
        coupling = [(0,1), (1,2), (2,3), (4,5), (5,6), (6,7), (8,9),
        (9,10), (10,11), (12,13), (13,14), (14,15), (0,4), (4,8),
        (8,12), (1,5), (5,9), (9,13), (2,6), (6,10), (10,14),
        (3,7), (7,11), (11,15)]
        if circuit_info == "qcnn/8-4-2.qasm" or circuit_info == "qcnn_sabre/8.qasm" or circuit_info == "qcnn_tket/8.qasm" or circuit_info == "qcnn/8.qasm":
            coupling += [(11, 14), (10, 13), (6, 11)]
        elif circuit_info == "qcnn/10-5-3-2.qasm" or circuit_info == "qcnn_sabre/10.qasm" or circuit_info == "qcnn_tket/10.qasm" or circuit_info == "qcnn/10.qasm":
            coupling += [(8, 13), (10, 13), (4, 9), (6, 11), (6, 9)]
        elif circuit_info == "qcnn/12-6-3-2.qasm" or circuit_info == "qcnn_sabre/12.qasm" or circuit_info == "qcnn_tket/12.qasm" or circuit_info == "qcnn/12.qasm":
            coupling += [(9, 12), (1, 4), (10, 13), (4, 9), (7, 10), (5, 10)]
        else:
            raise ValueError("Invalid circuit")
    else:
        raise ValueError("Invalid circuit")
    return coupling