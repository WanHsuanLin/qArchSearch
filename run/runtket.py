from pytket.routing import Architecture
from pytket import Circuit
from pytket.routing import route
from pytket.qasm import circuit_to_qasm, circuit_from_qasm
from pytket.extensions.qiskit import qiskit_to_tk, tk_to_qiskit
from qiskit import QuantumCircuit
from qiskit.converters import circuit_to_dag
import argparse
import time
import json
from pytket.circuit import Circuit, CustomGateDef
from sympy import symbols

def get_device(device: int):
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


def calExactDepth(gates:list,gate_spec:list):
    d = [0] * 16
    cg = ["swap"] * 16
    for pos, gtype in zip(gates,gate_spec):
        # print(gtype)
        if gtype == "swap":
            d[pos[0]] = max(d[pos[0]],d[pos[1]])+3
        elif gtype == "cx":
            if cg[pos[0]] == cg[pos[1]]:
                if cg[pos[0]] == "swap":
                    d[pos[0]] = max(d[pos[0]],d[pos[1]])+7
                elif cg[pos[0]] == "cx":
                    d[pos[0]] = max(d[pos[0]],d[pos[1]])+6
                else:
                    assert(False)
            elif (cg[pos[0]] == "swap") and (cg[pos[1]] == "cx"):
                d[pos[0]] = max(d[pos[0]]+7,d[pos[1]]+6)
            elif (cg[pos[0]] == "cx") and (cg[pos[1]] == "swap"):
                d[pos[0]] = max(d[pos[0]]+6,d[pos[1]]+7)
            else:
                assert (False)    
        else:
            assert (False)
        d[pos[1]] = d[pos[0]]
        cg[pos[0]] = gtype
        cg[pos[1]] = gtype
    return max(d)

# Initialize parser
parser = argparse.ArgumentParser()
# Adding optional argument
parser.add_argument("benchmark", metavar='B', type=str,
    help="Benchmark Set: arith or qaoa or qcnn")
parser.add_argument("device", metavar='D', type=int,
    help="Device graph: from -1 to 33")
parser.add_argument("folder", metavar='F', type=str,
    help="the folder to store results")
parser.add_argument("--size", dest="size", type=int,
    help="The size of the qaoa circuit: 8, 10, 12, 14, 16")
parser.add_argument("--trial", dest="trial", type=int,
    help="The index of qaoa circuit: from 0 to 9")
parser.add_argument("--filename", dest="filename", type=str,
    help="The file name of the arith circuit")
parser.add_argument("--lookahead", dest="iflookahead", action='store_true',
    help="if you want to use lookahead as the objective")
parser.add_argument("--decay", dest="ifdecay", action='store_true',
    help="if you want to use decay as the objective")
parser.add_argument("--comment", dest="comment", type=str,
    help="if you want to comment this run in any way")
# Read arguments from command line
args = parser.parse_args()

# default using the number of SWAP as objective
my_objective = "default"
# if args.iflookahead:
#     my_objective = "lookahead"
# if args.ifdecay:
#     my_objective = "decay"

# read qasm
qc = QuantumCircuit.from_qasm_file(args.filename)
circuit = qiskit_to_tk(qc)

# circuit = circuit_from_qasm(args.filename)
device = get_device(device=args.device)
resulted_circuit = route(circuit, Architecture(device))

qc_qikit = tk_to_qiskit(resulted_circuit)
qc_qikit.draw(scale=0.7, filename="tket.png", output='mpl', style='color')
gates = []
gate_spec = []
for gate in qc_qikit.data:
    # print('\ngate name:', gate[0].name)
    # print(type(gate[0].name))
    gate_spec += [(gate[0].name)]
    gates += [(gate[1][0].index, gate[1][1].index)]
    # print(gate[1][0].index)
    # print(gate[1][1].index)
    # print('qubit(s) acted on:', gate[1])
    # print('other paramters (such as angles):', gate[0].params)

qc_qikit = circuit_to_dag(qc_qikit)
D = qc_qikit.depth()
program_out = ""
g2 = 0
g1 = 0
g2r = len(qc_qikit.twoQ_gates())
g1r = len(qc_qikit.gate_nodes())-len(qc_qikit.twoQ_gates())
for node in qc_qikit.gate_nodes():
    if len(node.qargs) == 2:
        # program_out += f"{results[1][layer][gate]} {results[2][layer][gate][0]} {results[2][layer][gate][1]}\n"
        g2 += 1
    else:
        # program_out += f"{results[1][layer][gate]} {results[2][layer][gate][0]}\n"
        g1 += 1

# print("g2 = ",g2)
# print("g1 = ",g1)

# print("g2r = ",g2r)
# print("g1r = ",g1r)
if args.benchmark == "qcnn":
    g2 *= 3
    D = calExactDepth(gates,gate_spec)

info = dict()
info["M"] = qc_qikit.num_qubits()
info["D"] = D
info["g1"] = g1
info["g2"] = g2
info["device"] = args.device
info["benchmark"] = args.benchmark
if args.benchmark == "qcnn":
    info["size"] = args.filename.split('_')[0]
elif args.benchmark == "arith":
    info["file"] = args.filename.split('.')[0]
else:
    info["size"] = args.size
    info["trial"] = args.trial
info["gates"] = gates
info["gate_spec"] = gate_spec
# info["initial_mapping"] = results[3]
# info["final_mapping"] = results[4]
# info["objective_value"] = results[5]
info["coupling_graph"] = get_char_graph(device)
# info["olsq_mode"] = my_mode
info["tket_setting"] = my_objective
info["comment"] = "" + str(args.comment)
with open(f"./{args.folder}/{int(time.time()*1000) % 100000000000}.json", 
    'w') as file_object:
    json.dump(info, file_object)
