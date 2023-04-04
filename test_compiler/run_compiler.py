from platform import architecture
from qiskit.transpiler import CouplingMap
from qiskit import QuantumCircuit
from qiskit.transpiler import PassManager
from qiskit.transpiler.passes import SabreLayout
from qiskit.converters import *

from pytket.architecture import Architecture
from pytket.qasm import circuit_from_qasm
from pytket.mapping import MappingManager
from pytket.mapping import LexiLabellingMethod, LexiRouteRoutingMethod
from pytket.extensions.qiskit import qiskit_to_tk, tk_to_qiskit

# from pytket.routing import Architecture
# from pytket.predicates import CompilationUnit, ConnectivityPredicate
# from pytket.passes import SequencePass, RoutingPass, DecomposeSwapsToCXs
# from pytket.routing import GraphPlacement

def run_sabre(benchmark, circuit_info, coupling, count_physical_qubit):
    # read qasm
    if benchmark == "qcnn":
        qc = QuantumCircuit.from_qasm_file(circuit_info)
    elif benchmark == "qaoa":
        qc = QuantumCircuit(count_physical_qubit)
        for gate in circuit_info[1]:
            qc.rzz(1.0, gate[0], gate[1])
    # qc.draw(scale=0.7, filename = "cir.png", output='mpl', style='color')
    device = CouplingMap(couplinglist = coupling, description="sabre_test")
    # initialize sabre
    sb = SabreLayout(coupling_map = device, seed = 0)
    pass_manager = PassManager(sb)
    sabre_cir = pass_manager.run(qc)
    # sabre_cir.draw(scale=0.7, filename="sabrecir.png", output='mpl', style='color')
    gates = []
    gate_spec = []
    for gate in sabre_cir.data:
        # print(gate[0].name)
        # print(gate[0].num_qubits)
        if gate[0].name == 'barrier':
            continue
        if gate[0].name == 'u4' or gate[0].name == 'U4' :
            gate_spec.append(["u4"])
            gates.append([(gate[1][0].index, gate[1][1].index)])
        elif gate[0].name == "rzz" :
            gate_spec.append(["ZZ"])
            gates.append([(gate[1][0].index, gate[1][1].index)])
        elif gate[0].name[0] == 'v':
            gate_spec.append([gate[0].name])
            gates.append([(gate[1][0].index,)])
        elif gate[0].name[0] == 'm':
            gate_spec.append([gate[0].name])
            gates.append([(gate[1][0].index,)])
        else:
            gate_spec.append(["SWAP"])
            gates.append([(gate[1][0].index, gate[1][1].index)])

    return (gates,gate_spec)

def run_tket(benchmark, circuit_info, coupling, count_physical_qubit):
    # https://github.com/CQCL/pytket/blob/main/examples/mapping_example.ipynb
    # read qasm
    if benchmark == "qcnn":
        # qc = QuantumCircuit.from_qasm_file(circuit_info)
        circuit = circuit_from_qasm(circuit_info)
    elif benchmark == "qaoa":
        qc = QuantumCircuit(count_physical_qubit)
        for gate in circuit_info[1]:
            qc.rzz(1.0, gate[0], gate[1])
    # qc.draw(scale=0.7, filename = "cir_for_tket.png", output='mpl', style='color')
        circuit = qiskit_to_tk(qc)
    architecture = Architecture(coupling)
    mapping_manager = MappingManager(architecture)
    lexi_label = LexiLabellingMethod()
    lexi_route = LexiRouteRoutingMethod(10)
    mapping_manager.route_circuit(circuit, [lexi_label, lexi_route])

    qc_qikit = tk_to_qiskit(circuit)
    # qc_qikit.draw(scale=0.7, filename = "tketcir.png", output='mpl', style='color')
    # qc_qikit.draw(scale=0.7, filename = "dcir.png", output='mpl', style='color')
    gates = []
    gate_spec = []
    for gate in qc_qikit.data:
        # print(gate[0].name)
        # print(gate[0].num_qubits)
        if gate[0].name == 'barrier':
            continue
        elif gate[0].name == "rzz" :
            gate_spec.append(["ZZ"])
            gates.append([(gate[1][0].index, gate[1][1].index)])
        elif gate[0].name == 'rx':
            p = str(int(gate[0].params[0]))
            gate_spec.append(["v"+p])
            gates.append([(gate[1][0].index,)])
        elif gate[0].name == 'u1':
            p = str(int(gate[0].params[0]))
            gate_spec.append(["m"+p])
            gates.append([(gate[1][0].index,)])
        # elif gate[0].name == "SWAP":
        elif gate[0].name == "swap" or gate[0].name == "SWAP":
            gate_spec.append(["SWAP"])
            gates.append([(gate[1][0].index, gate[1][1].index)])
        else:
            gate_spec.append(["u4"])
            gates.append([(gate[1][0].index, gate[1][1].index)])
    # print(gate_spec)
    return (gates,gate_spec)

