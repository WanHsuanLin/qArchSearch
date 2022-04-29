from platform import architecture
from qiskit.transpiler import CouplingMap
from qiskit import QuantumCircuit
from qiskit.transpiler import PassManager
from qiskit.transpiler.passes import SabreSwap
from qiskit.converters import *

from pytket.architecture import Architecture
from pytket.mapping import MappingManager
from pytket.mapping import LexiLabellingMethod, LexiRouteRoutingMethod
from pytket.extensions.qiskit import qiskit_to_tk, tk_to_qiskit

# from pytket.routing import Architecture
# from pytket.predicates import CompilationUnit, ConnectivityPredicate
# from pytket.passes import SequencePass, RoutingPass, DecomposeSwapsToCXs
# from pytket.routing import GraphPlacement

def run_sabre(benchmark, circuit_info, coupling, objective):
    # read qasm
    if benchmark == "qcnn":
        qc = QuantumCircuit.from_qasm_file(circuit_info)
    elif benchmark == "qaoa":
        qc = QuantumCircuit(circuit_info[0])
        for gate in circuit_info[1]:
            qc.rzz(1.0, gate[0], gate[1])
    qc.draw(scale=0.7, filename = "cir.png", output='mpl', style='color')
    device = CouplingMap(couplinglist = coupling, description="sabre_test")
    # initialize sabre
    sb = SabreSwap(coupling_map = device, heuristic = objective, seed = 0)
    pass_manager = PassManager(sb)
    sabre_cir = pass_manager.run(qc)
    sabre_cir.draw(scale=0.7, filename="sabrecir.png", output='mpl', style='color')
    gates = []
    gate_spec = []
    for gate in sabre_cir.data:
        if gate[0].name == 'u4' or gate[0].name == 'U4' :
            gate_spec.append(["u4"])
        else:
            gate_spec.append(["SWAP"])
        gates.append([(gate[1][0].index, gate[1][1].index)])

    return (gates,gate_spec)

def run_tket(benchmark, circuit_info, coupling):
    # https://github.com/CQCL/pytket/blob/main/examples/mapping_example.ipynb
    # read qasm
    if benchmark == "qcnn":
        qc = QuantumCircuit.from_qasm_file(circuit_info)
    elif benchmark == "qaoa":
        qc = QuantumCircuit(circuit_info[0])
        for gate in circuit_info[1]:
            qc.rzz(1.0, gate[0], gate[1])
    qc.draw(scale=0.7, filename = "cir_for_tket.png", output='mpl', style='color')
    circuit = qiskit_to_tk(qc)
    architecture = Architecture(coupling)
    mapping_manager = MappingManager(architecture)
    lexi_label = LexiLabellingMethod()
    lexi_route = LexiRouteRoutingMethod(10)
    mapping_manager.route_circuit(circuit, [lexi_label, lexi_route])

    qc_qikit = tk_to_qiskit(circuit)
    qc_qikit.draw(scale=0.7, filename = "tketcir.png", output='mpl', style='color')
    gates = []
    gate_spec = []
    for gate in qc_qikit.data:
        if gate[0].name == 'cx':
            gate_spec.append(["u4"])
        else:
            gate_spec.append(["SWAP"])
        gates.append([(gate[1][0].index, gate[1][1].index)])
    # print(gate_spec)
    return (gates,gate_spec)

