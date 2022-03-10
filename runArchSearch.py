from qArchSearc.olsq import qArchEval
from qArchSearc.olsq.device import qcDeviceSet
import argparse
import json
import math

from qArchSearc.device import get_device_set
from qArchSearc.util import get_qaoa_graph


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
parser.add_argument("--tran", dest="iftran", action='store_true',
    help="if you want to use TB-OLSQ rather than OLSQ")
args = parser.parse_args()

# defulat using TB-OLSQ 
my_mode = "normal"
if args.iftran:
    my_mode = "transition"

lsqc_searcher = qArchEval(mode=my_mode)

lsqc_searcher.setdevice(get_device_set(benchmark=args.benchmark))

if args.benchmark == "qaoa":
    program = [args.size,
        get_qaoa_graph(size=args.size, trial=args.trial),
        ["ZZ" for _ in range( (args.size * 3) // 2 )] ]
    lsqc_searcher.setprogram(program, "IR")
else:
    file = open(args.filename)
    lsqc_searcher.setprogram(file.read())
    file.close()

results = lsqc_searcher.search(output_mode="IR")

for i, result in enumerate(results):
    with open(f"./{args.folder}/extra_edge_{i}.json", 'w') as file_object:
        json.dump(result, file_object)