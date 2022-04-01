from qArchSearc.olsq import qArchEval
from qArchSearc.olsq.device import qcDeviceSet
import argparse
import json
import math

from qArchSearc.device import get_device_set
from qArchSearc.util import get_qaoa_graph
#from memory_profiler import memory_usage

if __name__ == "__main__":
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
    parser.add_argument("--memory_max_size", dest="memory_max_size", type=int, default=0,
        help="set hard upper limit for memory consumption (G)")
    parser.add_argument("--verbose", dest="verbose", type=int, default=0,
        help="verbose level for Z3")
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
        lsqc_searcher.setprogram(args.benchmark, program, "IR")
    else:
        file = open(args.filename)
        lsqc_searcher.setprogram(args.benchmark, file.read())
        file.close()

    #mem_usage = memory_usage(f)
    print("start searching...")
    results = lsqc_searcher.search(memory_max_size=args.memory_max_size*1000, verbose=args.verbose)

    for i, result in enumerate(results):
        with open(f"./{args.folder}/extra_edge_{i}.json", 'w') as file_object:
            if args.benchmark == "qcnn":
                result["size"] = args.filename.split('_')[0]
            elif argsbenchmark == "arith":
                result["file"] = args.filename.split('.')[0]
            else:
                result["size"] = args.size
            json.dump(result, file_object)
