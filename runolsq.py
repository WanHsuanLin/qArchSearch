from qArchSearc.olsq import OLSQ
from qArchSearc.olsq.device import qcdevice
import argparse
import json
import math

from qArchSearc.device import get_device
from qArchSearc.util import get_qaoa_graph, get_qv_cir


# Initialize parser
parser = argparse.ArgumentParser()
# Adding optional argument
parser.add_argument("benchmark", metavar='B', type=str,
    help="Benchmark Set: arith or qaoa or qcnn or qv")
parser.add_argument("folder", metavar='F', type=str,
    help="the folder to store results")
parser.add_argument("--size", dest="size", type=int,
    help="The size of the qaoa circuit: 8, 10, 12, 14, 16")
parser.add_argument("--trial", dest="trial", type=int,
    help="The index of qaoa circuit: from 0 to 9")
parser.add_argument("--filename", dest="filename", type=str,
    help="The file name of the arith circuit")
parser.add_argument("--normal", dest="ifnormal", action='store_true',
    help="if you want to use OLSQ rather than TB-OLSQ")
parser.add_argument("--solve_opt", dest="solve_opt", type=int,
    help="use 1: optmization solve; 2: binary search SAT check; 3: incremental search; 4: incremental adding constraints")
parser.add_argument("--comment", dest="comment", type=str,
    help="if you want to comment this run in any way")
args = parser.parse_args()

# defulat using TB-OLSQ 
my_mode = "transition"
if args.ifnormal:
    my_mode = "normal"

lsqc_solver = OLSQ(mode=my_mode)

lsqc_solver.setdevice(
    get_device(device=args.device, benchmark=args.benchmark, fidelity = args.iffidelity))

if args.benchmark == "qaoa":
    program = [args.size,
        get_qaoa_graph(size=args.size, trial=args.trial),
        ["ZZ" for _ in range( (args.size * 3) // 2 )] ]
    lsqc_solver.setprogram(program, "IR")
elif args.benchmark == "qv":
    lsqc_solver.setdependency([])
    cir = get_qv_cir(size=args.size)
    # print(math.log(args.size,2))
    program = [int(math.log(args.size,2)),
        cir,
        ['u4' for _ in range(len(cir))] ]
    lsqc_solver.setprogram(program, "IR")
    lsqc_solver.setdependency([])
else:
    file = open(args.filename)
    lsqc_solver.setprogram(file.read())
    file.close()


lsqc_solver.solve(output_mode="IR")

with open(f"./{args.folder}/{output_file_name}.json", 'w') as file_object:
    json.dump(info, file_object)