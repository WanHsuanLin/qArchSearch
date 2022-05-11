import argparse
from qArchSearch.olsq.util import get_qaoa_graph
from qArchSearch.gate_absorption import run_only_gate_absorption
from test_compiler.olsq.solve import OLSQ
from test_compiler.olsq.device import qcdevice
import csv
import json

def create_list_from_data(data, coupling, count_physical_qubit):
    # print(data)
    run_only_gate_absorption(data["benchmark"], data, coupling, count_physical_qubit)
    data_list = []  # create an empty list
    # append the items to the list in the same order.
    data_list.append(data.get('mode'))
    data_list.append(data.get('#e'))
    data_list.append(data.get('M'))
    data_list.append(data.get('gates'))
    data_list.append(data.get('gate_spec'))
    data_list.append(data.get('coupling'))
    return data_list

def run_olsq_tbolsq(benchmark, circuit_info, coupling, count_physical_qubit, mode):
    lsqc_solver = OLSQ(objective_name="swap", mode=mode)
    if benchmark == "qcnn":
        file = open(circuit_info)
        lsqc_solver.setprogram("qcnn", file.read())
        file.close()
        measurement = dict()
        single_qubit_gate = dict()
        for i, gname in enumerate(lsqc_solver.list_gate_name):
            if gname[0] == 'v':
                single_qubit_gate[int(gname[1:])] = i
            elif gname[0] == 'm':
                measurement[int(gname[1:])] = i
        dependency = []
        for key in measurement:
            dependency.append((measurement[key], single_qubit_gate[key]))
        lsqc_solver.setdependency(dependency)
        # print(dependency)

    elif benchmark == "qaoa":
        program = [circuit_info[0],
            circuit_info[1],
            ["ZZ" for _ in range( (circuit_info[0] * 3) // 2 )] ]
        lsqc_solver.setprogram("qaoa", program, "IR")

    device = qcdevice(name="none", nqubits=count_physical_qubit, connection=coupling, swap_duration=1)
    lsqc_solver.setdevice(device)
    result = lsqc_solver.solve(output_mode="IR", memory_max_size=0, verbose=0)
    return result

if __name__ == "__main__":
    # Initialize parser
    parser = argparse.ArgumentParser()
    # Adding optional argument
    parser.add_argument("device_set", metavar='DS', type=str,
        help="Device: hh: heavy-hexagonal (IBM), grid: sqaure")
    parser.add_argument("device_spec", metavar='DS', type=str,
        help="file to store device spec")
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
        tmp = args.device_spec.split('/')[-1].split('.')[0]
        csv_name = args.folder+"/"+tmp+"_optimal_"+args.filename[5:-4]+"csv"
    elif args.benchmark == "qaoa":
        circuit_info = (args.size, get_qaoa_graph(args.size, args.trial), args.trial)
        tmp = args.device_spec.split('/')[-1].split('.')[0]
        csv_name = args.folder+"/"+tmp+"_optimal_"+str(args.size)+"_"+str(args.trial)+".csv"

    if args.device_set == "hh":
        count_physical_qubit = 18
        fix_coupling = [(0,4), (1,2), (2,3), (3,4), (4,5), (5,6), (6,7), 
                    (2,8), (6,9), (10,11), (8,11), (11,12), (12,13), 
                    (13,14), (14,15), (15,16), (9,15), (13,17)]
    elif args.device_set == "grid":
        count_physical_qubit = 16
        fix_coupling = [(0,1), (1,2), (2,3), (4,5), (5,6), (6,7), (8,9),
        (9,10), (10,11), (12,13), (13,14), (14,15), (0,4), (4,8),
        (8,12), (1,5), (5,9), (9,13), (2,6), (6,10), (10,14),
        (3,7), (7,11), (11,15)]
    else:
        raise ValueError("invalid device_set name\n")

    with open(args.device_spec) as f:
        device_spec = json.load(f)

    # with open(csv_name, 'w+') as c:
    #     writer = csv.writer(c)
    #     writer.writerow(['mode', '#e','M', 'gates', 'gate_spec', 'coupling'])

    data = dict()
    data["benchmark"] = args.benchmark
    
    # test_set = [6,7]
    # for key in test_set:
    for key in range(17):
        str_key = str(key)
        if str_key not in device_spec.keys():
            break
        coupling = []
        for edge in device_spec[str_key]:
            coupling.append((edge[0], edge[1]))
        coupling += fix_coupling
        # for mode in ["transition", 'normal']:
        for mode in ['normal']:
            data = run_olsq_tbolsq(args.benchmark, circuit_info, coupling, count_physical_qubit, mode)
            data["#e"] = int(key)
            data["coupling"] = device_spec[str_key]
            data["mode"] = mode
            data_list = create_list_from_data(data, coupling, count_physical_qubit)
            with open(csv_name, 'a') as c:
                writer = csv.writer(c)
                writer.writerow(data_list)
    
