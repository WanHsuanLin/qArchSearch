import argparse
from test_compiler.run_compiler import run_tket, run_sabre
from qArchSearch.olsq.util import get_qaoa_graph
from qArchSearch.gate_absorption import run_only_gate_absorption
import csv
import json


def create_list_from_data(data, coupling, count_physical_qubit):
    # run_only_gate_absorption(data["benchmark"], data, coupling, count_physical_qubit)
    data_list = []  # create an empty list
    # append the items to the list in the same order.
    data_list.append(data.get('compiler'))
    data_list.append(data.get('#e'))
    data_list.append(data.get('M'))
    data_list.append(data.get('gates'))
    data_list.append(data.get('gate_spec'))
    data_list.append(data.get('coupling'))
    return data_list


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
        filename=args.filename.split('/')
        circuit_info_sabre=filename[0]+"_sabre/"+filename[1]
        circuit_info_tket=filename[0]+"_tket/"+filename[1]
        csv_name = args.folder+"/"+args.device_set+"_heuristic_"+filename[-1][:-5]
        program_qubit=int(filename[-1][:-5])
    elif args.benchmark == "qaoa":
        program_qubit = args.size
        circuit_info_sabre = (args.size, get_qaoa_graph(args.size, args.trial), args.trial)
        circuit_info_tket = circuit_info_sabre
        csv_name = args.folder+"/"+args.device_set+"_heuristic_"+str(args.size)+"_"+str(args.trial)
    else:
        raise ValueError("invalid benchmark name\n")

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

    # csv_name1 = csv_name + "_sabre.csv" 
    # with open(csv_name1, 'w+') as c:
    #     writer = csv.writer(c)
    #     writer.writerow(['compiler', '#e','M', '#gates', 'gate_spec', 'coupling'])

    data = dict()
    data["benchmark"] = args.benchmark
    data["M"]=program_qubit

    # for key in range(17):
    #     str_key = str(key)
    #     if str_key not in device_spec.keys():
    #         break
    #     data["#e"] = int(key)
    #     data["coupling"] = device_spec[str_key]
    #     coupling = []
    #     for edge in device_spec[str_key]:
    #         coupling.append((edge[0], edge[1]))
    #     coupling += fix_coupling
    #     for objective in ["basic", "lookahead", "decay"]:
    #         data["compiler"] = "sabre_"+objective
    #         data["gates"], data["gate_spec"] = run_sabre(args.benchmark, circuit_info_sabre, coupling, objective, count_physical_qubit)
    #         data_list = create_list_from_data(data, coupling, count_physical_qubit)
    #         with open(csv_name1, 'a') as c:
    #             writer = csv.writer(c)
    #             writer.writerow(data_list)
    
    csv_name2 = csv_name + "_tket.csv" 
    with open(csv_name2, 'w+') as c:
        writer = csv.writer(c)
        writer.writerow(['compiler', '#e','M', 'gates', 'gate_spec', 'coupling'])

    for key in range(17):
        str_key = str(key)
        if str_key not in device_spec.keys():
            break
        data["#e"] = int(key)
        data["coupling"] = device_spec[str_key]
        coupling = []
        for edge in device_spec[str_key]:
            coupling.append((edge[0], edge[1]))
        coupling += fix_coupling
        data["gates"], data["gate_spec"] = run_tket(args.benchmark, circuit_info_tket, coupling, count_physical_qubit)
        data["compiler"] = "tket"
        data_list = create_list_from_data(data, coupling, count_physical_qubit)
        with open(csv_name2, 'a') as c:
            writer = csv.writer(c)
            writer.writerow(data_list)
    
