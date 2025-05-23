from qArchSearch.search import qArchSearch
import argparse

from qArchSearch.devices.device import get_device_set_hh, get_device_set_square_4by4
from qArchSearch.util import get_qaoa_graph
#from memory_profiler import memory_usage


for size in [10, 12, 16]:
    arch_searcher = qArchSearch()

    # arch_searcher.setdevice(get_device_set_hh())

    arch_searcher.setdevice(get_device_set_square_4by4())

    program = [size,
        get_qaoa_graph(size=size, trial=0),
        ["ZZ" for _ in range( (size * 3) // 2 )] ]
    print(program)
    arch_searcher.setprogram("qaoa", program, "IR")

    #mem_usage = memory_usage(f)
    results = arch_searcher.dump("cnf", bound_depth = 5, bound_swap = 10, bound_edge = 1)
    results = arch_searcher.dump("cnf", bound_depth = 5, bound_swap = 10, bound_edge = 2)
    results = arch_searcher.dump("cnf", bound_depth = 5, bound_swap = 10, bound_edge = 3)

    results = arch_searcher.dump("cnf", bound_depth = 5, bound_swap = 5, bound_edge = 1)
    results = arch_searcher.dump("cnf", bound_depth = 5, bound_swap = 5, bound_edge = 2)
    results = arch_searcher.dump("cnf", bound_depth = 5, bound_swap = 5, bound_edge = 3)

    # for i, result in enumerate(results):
    #     with open(f"./{args.folder}/extra_edge_{i}.json", 'a') as file_object:
    #         if args.benchmark == "qcnn":
    #             result["size"] = args.filename.split('_')[0]
    #         elif args.benchmark == "arith":
    #             result["file"] = args.filename.split('.')[0]
    #         else:
    #             result["size"] = args.size
    #         json.dump(result, file_object)
