from qArchSearch.search import qArchSearch
import argparse

from qArchSearch.devices.device import get_device_set_hh, get_device_set_square_4by4
from qArchSearch.util import get_qaoa_graph
#from memory_profiler import memory_usage

if __name__ == "__main__":
    # Initialize parser
    parser = argparse.ArgumentParser()
    # Adding optional argument
    parser.add_argument("device_set", metavar='DS', type=str,
        help="Device base: hh: heavy-hexagonal (IBM), grid: sqaure")
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
    parser.add_argument("--memory_max_size", dest="memory_max_size", type=int, default=0,
        help="set hard upper limit for memory consumption (G)")
    parser.add_argument("--verbose", dest="verbose", type=int, default=0,
        help="verbose level for Z3")
    args = parser.parse_args()

    arch_searcher = qArchSearch()

    if args.device_set == "hh":
        arch_searcher.setdevice(
            get_device_set_hh())
    else:
        arch_searcher.setdevice(
            get_device_set_square_4by4())

    if args.benchmark == "qaoa":
        program = [args.size,
            get_qaoa_graph(size=args.size, trial=args.trial),
            ["ZZ" for _ in range( (args.size * 3) // 2 )] ]
        arch_searcher.setprogram(args.benchmark, program, "IR")
    else:
        file = open(args.filename)
        arch_searcher.setprogram(args.benchmark, file.read())
        file.close()

    #mem_usage = memory_usage(f)
    results = arch_searcher.search(args.folder, memory_max_size=args.memory_max_size*1000, verbose=args.verbose)

    # for i, result in enumerate(results):
    #     with open(f"./{args.folder}/extra_edge_{i}.json", 'a') as file_object:
    #         if args.benchmark == "qcnn":
    #             result["size"] = args.filename.split('_')[0]
    #         elif args.benchmark == "arith":
    #             result["file"] = args.filename.split('.')[0]
    #         else:
    #             result["size"] = args.size
    #         json.dump(result, file_object)
