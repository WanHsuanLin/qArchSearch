import argparse
from test_compiler.best_device import get_best_coupling_hh, get_best_coupling_grid
from qArchSearch.olsq.util import get_qaoa_graph
from qArchSearch.olsq.util import cal_crosstalk, cal_fidelity
from qArchSearch.gate_absorption import run_gate_absorption
from test_compiler.olsq.solve import OLSQ
from test_compiler.olsq.device import qcdevice
import csv


def create_list_from_data(data, coupling, count_physical_qubit):
    run_gate_absorption(data["benchmark"], data, coupling, count_physical_qubit)
    data['crosstalk'] = cal_crosstalk(data, data["benchmark"], coupling, count_physical_qubit)
    data['fidelity'], data['fidelity_ct']  = cal_fidelity(data)

    data_list = []  # create an empty list
    # append the items to the list in the same order.
    data_list.append(data.get('comiler'))
    data_list.append(data.get('M'))
    data_list.append(data.get('D'))
    data_list.append(data.get('g1'))
    data_list.append(data.get('g2'))
    data_list.append(data.get('fidelity'))
    data_list.append(data.get('crosstalk'))
    data_list.append(data.get('fidelity_ct'))
    data_list.append(data.get('gates'))
    data_list.append(data.get('gate_spec'))

def run_olsq_tbolsq(benchmark, circuit_info, coupling, count_physical_qubit, mode):
    lsqc_solver = OLSQ(objective_name="swap", mode=mode)
    if benchmark == "qcnn":
        file = open(circuit_info)
        lsqc_solver.setprogram("qcnn", file.read())
        file.close()
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
        help="Device: hh: heavy-hexagonal (IBM), grid: sqaure, bhh, bgrid")
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
        csv_name = args.folder+"/"+args.device_set+"_optimal_"+args.filename[5:-4]
    elif args.benchmark == "qaoa":
        circuit_info = (args.size, get_qaoa_graph(args.size, args.trial), args.trial)
        csv_name = args.folder+"/"+args.device_set+"_optimal_"+args.size+"_"+args.trial

    if args.device_set == "hh":
        count_physical_qubit = 18
        coupling = get_best_coupling_hh(circuit_info)
    elif args.device_set == "bhh":
        count_physical_qubit = 18
        coupling = [(0,4), (1,2), (2,3), (3,4), (4,5), (5,6), (6,7), 
                    (2,8), (6,9), (10,11), (8,11), (11,12), (12,13), 
                    (13,14), (14,15), (15,16), (9,15), (13,17)]
    elif args.device_set == "grid":
        count_physical_qubit = 16
        coupling = get_best_coupling_grid(circuit_info)
    else:
        count_physical_qubit = 16
        coupling = [(0,1), (1,2), (2,3), (4,5), (5,6), (6,7), (8,9),
        (9,10), (10,11), (12,13), (13,14), (14,15), (0,4), (4,8),
        (8,12), (1,5), (5,9), (9,13), (2,6), (6,10), (10,14),
        (3,7), (7,11), (11,15)]


    with open(csv_name, 'w+') as c:
        writer = csv.writer(c)
        writer.writerow(['compiler','M', 'D', 'g1', 'g2', 'f', 'crosstalk', 'f_ct', '#gates', 'gate_spec'])

    data = dict()
    data["benchmark"] = args.benchmark
    
    for mode in ["transition", 'mixed']:
        data = run_olsq_tbolsq(args.benchmark, circuit_info, coupling, count_physical_qubit, mode)
        data_list = create_list_from_data(data, coupling, count_physical_qubit)
        with open(csv_name, 'a') as c:
            writer = csv.writer(c)
            writer.writerow(data_list)
    
