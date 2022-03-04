from olsq import OLSQ
from olsq.device import qcdevice
import argparse
import time
import json

from run.device import get_deviceND
from run.device import get_char_graph

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
    [(4, 12), (4, 8), (4, 1), (12, 1), (12, 9), (0, 2), (0, 10), (0, 13), (2, 5), (2, 10), (9, 11), (9, 5), (11, 3), (11, 5), (1, 7), (7, 13), (7, 8), (13, 6), (8, 3), (3, 6), (6, 10)]]
    }

    return qaoa[str(size)][trial]

def calExactDepth(data:dict):
    d = [0] * 16
    cg = ["SWAP"] * 16
    for gate_pos, gate_type in zip(data["gates"],data["gate_spec"]):
        for pos, gtype in zip(gate_pos, gate_type):
            if gtype == "SWAP":
                d[pos[0]] = max(d[pos[0]],d[pos[1]])+3
            elif gtype == "u4":
                if cg[pos[0]] == cg[pos[1]]:
                    if cg[pos[0]] == "SWAP":
                        d[pos[0]] = max(d[pos[0]],d[pos[1]])+7
                    elif cg[pos[0]] == "u4":
                        d[pos[0]] = max(d[pos[0]],d[pos[1]])+6
                    else:
                        assert(False)
                elif (cg[pos[0]] == "SWAP") and (cg[pos[1]] == "u4"):
                    d[pos[0]] = max(d[pos[0]]+7,d[pos[1]]+6)
                elif (cg[pos[0]] == "u4") and (cg[pos[1]] == "SWAP"):
                    d[pos[0]] = max(d[pos[0]]+6,d[pos[1]]+7)
                else:
                    assert (False)    
            else:
                assert (False)
            d[pos[1]] = d[pos[0]]
            cg[pos[0]] = gtype
            cg[pos[1]] = gtype
    data["D"] = max(d)

# Initialize parser
parser = argparse.ArgumentParser()
# Adding optional argument
parser.add_argument("benchmark", metavar='B', type=str,
    help="Benchmark Set: arith or qaoa or qcnn")
parser.add_argument("device", metavar='D', type=int,
    help="Device graph: from 0 to 255")
parser.add_argument("folder", metavar='F', type=str,
    help="the folder to store results")
parser.add_argument("--size", dest="size", type=int,
    help="The size of the qaoa circuit: 8, 10, 12, 14, 16")
parser.add_argument("--trial", dest="trial", type=int,
    help="The index of qaoa circuit: from 0 to 9")
parser.add_argument("--filename", dest="filename", type=str,
    help="The file name of the arith circuit")
parser.add_argument("--depth", dest="ifdepth", action='store_true',
    help="if you want to use depth as the objective")
parser.add_argument("--fidelity", dest="iffidelity", action='store_true',
    help="if you want to use fidelity as the objective")
parser.add_argument("--normal", dest="ifnormal", action='store_true',
    help="if you want to use OLSQ rather than TB-OLSQ")
parser.add_argument("--comment", dest="comment", type=str,
    help="if you want to comment this run in any way")
# Read arguments from command line
args = parser.parse_args()

# default using the number of SWAP as objective
my_objective = "swap"
if args.ifdepth:
    my_objective = "depth"
if args.iffidelity:
    my_objective = "fidelity"

# defulat using TB-OLSQ 
my_mode = "transition"
if args.ifnormal:
    my_mode = "normal"

lsqc_solver = OLSQ(objective_name=my_objective, mode=my_mode)

lsqc_solver.setdevice(
    get_deviceND(device=args.device, benchmark=args.benchmark, fidelity = args.iffidelity))


if args.benchmark == "qaoa":
    program = [args.size,
        get_qaoa_graph(size=args.size, trial=args.trial),
        ["ZZ" for _ in range( (args.size * 3) // 2 )] ]
    lsqc_solver.setprogram(program, "IR")
    lsqc_solver.setdependency([])
else:
    file = open(args.filename)
    lsqc_solver.setprogram(file.read())
    file.close()

results = lsqc_solver.solve(output_mode="IR")

D = results[0]
program_out = ""
g2 = 0
g1 = 0
for layer in range(results[0]):
    for gate in range(len(results[1][layer])):
        if len(results[2][layer][gate]) == 2:
            program_out += f"{results[1][layer][gate]} {results[2][layer][gate][0]} {results[2][layer][gate][1]}\n"
            g2 += 1
        else:
            program_out += f"{results[1][layer][gate]} {results[2][layer][gate][0]}\n"
            g1 += 1
# print(program_out)

# D=results[0]*3 for qaoa and qcnn; D=results[0] for arith
if args.benchmark == "qaoa" or args.benchmark == "qcnn":
    D *= 3
    # if qcnn g2 *= 3 since the gates are generic two-qubti gates
    g2 *= 3
if args.benchmark == "qaoa":
    # if qaoa each swap is triple and each ZZ-phase is double, so g2 = g2*3-#ZZ
    g2 -= (args.size * 3) // 2
    # there is a Rz gate in every ZZ-Phase
    g1 += (args.size * 3) // 2


info = dict()
info["M"] = lsqc_solver.count_program_qubit
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
info["gates"] = results[2]
info["gate_spec"] = results[1]
info["initial_mapping"] = results[3]
info["final_mapping"] = results[4]
info["objective_value"] = results[5]
info["coupling_graph"] = get_char_graph(lsqc_solver.device.list_qubit_edge)
info["olsq_mode"] = my_mode
info["olsq_obj"] = my_objective
info["comment"] = "" + str(args.comment)
if args.benchmark == "qcnn":
    calExactDepth(info)
with open(f"./{args.folder}/{int(time.time()*1000) % 100000000000}.json", 
    'w') as file_object:
 json.dump(info, file_object)
