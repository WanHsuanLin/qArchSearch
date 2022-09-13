[![jetcas](https://img.shields.io/badge/Published-JETCAS'22-brightgreen.svg?style=for-the-badge)](https://ieeexplore.ieee.org/abstract/document/9869862)
[![arXiv](https://img.shields.io/badge/arXiv-2207.14482-brightgreen.svg?style=for-the-badge)](https://arxiv.org/abs/2207.14482)

# Domain-Specific Quantum Architecture Optimization

Current quantum processors are crafted by human experts. 
These general-purpose architectures, however, leave room for customization and optimization, especially when targeting popular near-term QC applications. 
We present a framework for optimizing quantum architectures through customizing qubit connectivity to improve circuit fidelity. 
At the time of publication, we demonstrate up to 59% fidelity improvement in simulation by optimizing the heavy-hexagon architecture for QAOA maxcut circuits, and up to 14% improvement on the grid architecture. For the QCNN circuit, architecture optimization improves fidelity by 11% on the heavy-hexagon architecture and 605% on the grid architecture.

For more details on the theory and the experiments, please refer to [the paper](https://ieeexplore.ieee.org/abstract/document/9869862).
Below is a brief tutorial on how to use the package.

## Installation

```
python3 -m pip install qArchSearch
```
Please make sure that you have `networkx` version `>=2.5` and `z3-solver` version `>=4.8.9.0` in your Python environment.

## Initialization

```
from qArchSearch.search import qArchSearch

# initiate qArchSearch
arch_searcher = qArchSearch()
```
## Setting the architecture space

The architecture space is defined by (1) base architecture space, (2) flexible connections, and (3) flexible connection activation constraints

We are going to use the `setdevice` method.
We use a minimalist class `qcDeviceSet` to store the properties of the device that we need, which can be constructed with these arguments.
(The last three are only for fidelity optimization.)
- `name`
- `nqubits`: the number of physical qubits
- `connection`: a list of physical qubit pairs corresponding to edges in the base architecture
- `extra_connection`: a list of physical qubit pairs corresponding to flexible edges in the flexible edge set
- `conflict_coupling_set`: a list of pairs of qubit connections that cannot be actiavted at the same time


## Setting the Input Program

Apart from the architecture space, we need the quantum program/circuit to execute, which can be set with the `setprogram` method.
_To be safe, always set the device first and then the program._

In general, there are three ways to set the program: 
1. Use [OLSQ](https://github.com/tbcdebug/OLSQ) IR
2. Use a string in QASM format
3. Use an QASM file, e.g., one of programs used in the paper in `olsq/benchmarks/`.

```
circuit_str = "OPENQASM 2.0;\ninclude \"qelib1.inc\";\nqreg q[3];\nh q[2];\n" \
              "cx q[1], q[2];\ntdg q[2];\ncx q[0], q[2];\nt q[2];\n" \
              "cx q[1], q[2];\ntdg q[2];\ncx q[0], q[2];\nt q[1];\nt q[2];\n" \
              "cx q[0], q[1];\nh q[2];\nt q[0];\ntdg q[1];\ncx q[0], q[1];\n"

# input the quantum program as a QASM string
lsqc_solver.setprogram(circuit_str)
```

The example above is a Toffoli gate.
We can also load an QASM file of it.
```
# load one of the QASM files from olsq/benchmarks
lsqc_solver.setprogram("toffoli", input_mode="benchmark")

# load your own QASM file
# circuit_file = open("my-qasm-file", "r").read()

lsqc_solver.setprogram(circuit_file)

# Toffoli Gate:
#                                                        ┌───┐      
# q_0: ───────────────────■─────────────────────■────■───┤ T ├───■──
#                         │             ┌───┐   │  ┌─┴─┐┌┴───┴┐┌─┴─┐
# q_1: ───────■───────────┼─────────■───┤ T ├───┼──┤ X ├┤ TDG ├┤ X ├
#      ┌───┐┌─┴─┐┌─────┐┌─┴─┐┌───┐┌─┴─┐┌┴───┴┐┌─┴─┐├───┤└┬───┬┘└───┘
# q_2: ┤ H ├┤ X ├┤ TDG ├┤ X ├┤ T ├┤ X ├┤ TDG ├┤ X ├┤ T ├─┤ H ├──────
#      └───┘└───┘└─────┘└───┘└───┘└───┘└─────┘└───┘└───┘ └───┘      
"""
```

## Solving and Output

It can be seen that in the Toffoli gate above, there are two-qubit gates on pair `(q_0,q_1)`, `(q_1,q_2)`, and `(q_2,q_0)`.
However, there are no such triangles on device `ourense`.
This means that no matter how the qubits in the program are mapped to physical qubits, we need to insert SWAP gates.

```
# Optimize architecture for the input program LSQC
result = arch_searcher.search('optimized_devices')
```

The `search` method takes three arguments and two of them are optional.
- `folder`: forders to store the optimized architecture.
- `memory_max_size`: (optional) maximum memory use for SMT solver (default: no limit)
- `verbose`: (optional) verbose for z3 (default: no verbose information)

The result of the Toffoli example is shown below.
Note that a SWAP gate, decomposed into three CX gates, has been inserted.
```
# a LSQC solution to the Toffoli gate on device 'ourense'
#                                                  ┌───┐     ┌───┐┌───┐ ┌───┐      ┌─┐      
# q_0: ───────────────────■─────────────────────■──┤ X ├──■──┤ X ├┤ T ├─┤ H ├──────┤M├──────
#      ┌───┐┌───┐┌─────┐┌─┴─┐┌───┐┌───┐┌─────┐┌─┴─┐└─┬─┘┌─┴─┐└─┬─┘└───┘ ├───┤      └╥┘┌─┐   
# q_1: ┤ H ├┤ X ├┤ TDG ├┤ X ├┤ T ├┤ X ├┤ TDG ├┤ X ├──■──┤ X ├──■────■───┤ T ├───■───╫─┤M├───
#      └───┘└─┬─┘└─────┘└───┘└───┘└─┬─┘└┬───┬┘└───┘     └───┘     ┌─┴─┐┌┴───┴┐┌─┴─┐ ║ └╥┘┌─┐
# q_2: ───────■─────────────────────■───┤ T ├─────────────────────┤ X ├┤ TDG ├┤ X ├─╫──╫─┤M├
#                                       └───┘                     └───┘└─────┘└───┘ ║  ║ └╥┘
# q_3: ─────────────────────────────────────────────────────────────────────────────╫──╫──╫─
#                                                                                   ║  ║  ║
# q_4: ─────────────────────────────────────────────────────────────────────────────╫──╫──╫─
#                                                                                   ║  ║  ║
# c: 5/═════════════════════════════════════════════════════════════════════════════╩══╩══╩═
#                                                                                   2  0  1
```

## BibTeX Citation
```
@article{lin2022domain,
  title={Domain-Specific Quantum Architecture Optimization},
  author={Lin, Wan-Hsuan and Tan, Bochen and Niu, Murphy Yuezhen and Kimko, Jason and Cong, Jason},
  journal={IEEE Journal on Emerging and Selected Topics in Circuits and Systems},
  year={2022},
  publisher={IEEE}
}
```
