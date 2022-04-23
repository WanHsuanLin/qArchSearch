import argparse
import json
from test_compiler.run_compiler import run_tket, run_sabre, run_olsq_tbolsq
from test_compiler.best_device import get_best_coupling_hh, get_best_coupling_grid
from qArchSearch.olsq.util import get_qaoa_graph

if __name__ == "__main__":
    # Initialize parser
    parser = argparse.ArgumentParser()
    # Adding optional argument
    parser.add_argument("device_set", metavar='DS', type=str,
        help="Device base: hh: heavy-hexagonal (IBM), grid: sqaure")
    parser.add_argument("benchmark", metavar='B', type=str,
        help="Benchmark Set: arith or qaoa or qcnn")
    parser.add_argument("folder", metavar='F', type=str,
        help="the folder to store results")
    parser.add_argument("--size", dest="size", type=int,
        help="The size of the qaoa circuit: 8, 10, 12, 14, 16")
    parser.add_argument("--trial", dest="trial", type=int,
        help="The index of qaoa circuit: from 0 to 9")
    parser.add_argument("--filename", dest="filename", type=str,
        help="The file name of the arith circuit")
    # Read arguments from command line
    args = parser.parse_args()

    if args.benchmark == "qcnn":
        circuit_info = args.filename
    elif args.benchmark == "qaoa":
        circuit_info = (args.size, get_qaoa_graph(args.size, args.trial))

    if args.device_set == "hh":
        coupling = get_best_coupling_hh(circuit_info)
    else:
        coupling = get_best_coupling_grid(circuit_info)

    for objective in ["basic", "lookahead", "decay"]:
        gates, gate_spec = run_sabre(args.benchmark, circuit_info, coupling, objective)
    
    gates, gate_spec = run_tket(args.benchmark, circuit_info, coupling)
    
    for mode in ["transition", 'mixed']:
        result = run_olsq_tbolsq(args.benchmark, circuit_info, coupling, mode)


