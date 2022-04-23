from qiskit.transpiler import CouplingMap
from qiskit import QuantumCircuit
from qiskit.transpiler import PassManager
from qiskit.transpiler.passes import SabreSwap
from qiskit.converters import *
from olsq.solve import OLSQ
from olsq.device import qcdevice
from pytket.routing import Architecture
from pytket.routing import route
from pytket.extensions.qiskit import qiskit_to_tk, tk_to_qiskit

def run_sabre(benchmark, circuit_info, coupling, objective):
    # read qasm
    if benchmark == "qcnn":
        qc = QuantumCircuit.from_qasm_file(circuit_info)
    elif benchmark == "qaoa":
        qc = QuantumCircuit(circuit_info[0])
        for gate in circuit_info[1]:
            qc.rzz(1.0, gate[0], gate[1])
    qc.draw(scale=0.7, filename = "qc.png", output='mpl', style='color')
    device = CouplingMap(couplinglist = coupling, description="sabre_test")
    # initialize sabre
    sb = SabreSwap(coupling_map = device, heuristic = objective, seed = 0)
    pass_manager = PassManager(sb)
    sabre_cir = pass_manager.run(qc)
    sabre_cir.draw(scale=0.7, filename="sabrecir.png", output='mpl', style='color')
    gates = []
    gate_spec = []
    for gate in sabre_cir.data:
        gate_spec += [(gate[0].name)]
        gates += [(gate[1][0].index, gate[1][1].index)]

    return (gates,gate_spec)

def run_tket(benchmark, circuit_info, coupling):
    # read qasm
    if benchmark == "qcnn":
        qc = QuantumCircuit.from_qasm_file(circuit_info)
    elif benchmark == "qaoa":
        qc = QuantumCircuit(circuit_info[0])
        for gate in circuit_info[1]:
            qc.rzz(1.0, gate[0], gate[1])
    
    circuit = qiskit_to_tk(qc)
    tket_cir = route(circuit, Architecture(coupling))
    qc_qikit = tk_to_qiskit(tket_cir)

    gates = []
    gate_spec = []
    for gate in qc_qikit.data:
        gate_spec += [(gate[0].name)]
        gates += [(gate[1][0].index, gate[1][1].index)]

    return (gates,gate_spec)

def run_olsq_tbolsq(benchmark, circuit_info, coupling, mode):
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

    device = qcdevice(name="none", nqubits=33, connection=coupling, swap_duration=1)
    lsqc_solver.setdevice(device)
    result = lsqc_solver.solve(output_mode="IR", memory_max_size=0, verbose=0)
    return result