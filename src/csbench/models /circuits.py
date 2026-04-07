
"""Circuit generation module. All the circuits are generated with angles equal to zero."""

import sys

import numpy as np
from qibo import Circuit, gates

# We want to use mpstab's ansatze to tune the magic
from mpstab.models.ansatze import CircuitAnsatz

def hardware_efficient(nqubits:int, depth:int)->str:
    """
    Generate a simple string corresponding to an hardware efficient ansatz.
    This Hardware Efficient Ansatz consists of alternating layers of single-qubit RY rotations and CZ entangling gates.
    """
    circuit = Circuit(nqubits)
    for d in range(depth):
        for q in range(nqubits):
            circuit.add(gates.RY(q, theta=0.))
        for q in range(nqubits - 1):
            circuit.add(gates.CZ(q, q + 1)) 
    return circuit

def floquet_dynamics(nqubits:int, depth:int)->str:
    """Ciao"""
    pass

def generate_benchmark_circuits(
        ansatz_name:str, 
        nqubits:int,
        depth:int,
        n_circuits:int,
        rng_seed:int,
        magic_replacement_prob:float,
    )->tuple[str, list[str]]:
    """Generate a family of circuits which will be run to compute the statistics requirewd for the benchmark."""

    # Fixing seed to ensure reproducibility
    np.random.seed(rng_seed)

    # Check that the provided name corresponds to a valid ansatz function defined in this module
    if ansatz_name not in list(sys.modules[__name__].__dict__.keys()):
        raise ValueError(
            f"Ansatz {ansatz_name} not found. Available ansatze are: {list(sys.modules[__name__].__dict__.keys())}"
        )

    current_module = sys.modules[__name__]
    reference_circuit = getattr(current_module, ansatz_name)(nqubits, depth)



















### ------------------------------------------- Tia



def build_circuit_qasm(
    num_qubits: int, 
    num_layers: int, 
    J: float, 
    h: float, 
    b: float
) -> str:
    """
    Generates an OpenQASM 2.0 string for the forward-time Kicked Ising Floquet circuit.

    Parameters:
    - num_qubits (int): Total number of qubits in the 1D chain.
    - num_layers (int): Number of Floquet periods (t), where one period is an even+odd layer.
    - J (float): Theoretical Ising coupling strength.
    - h (float): Theoretical longitudinal field strength.
    - b (float): Theoretical transverse kick strength.
    
    Returns:
    - str: Valid OpenQASM 2.0 representation of the circuit.
    """
    if num_qubits < 2:
        raise ValueError("The circuit requires at least 2 qubits.")

    # Standard OpenQASM 2.0 headers
    qasm_lines = [
        "OPENQASM 2.0;",
        'include "qelib1.inc";',
        f"qreg q[{num_qubits}];"
    ]
    
    # Map physical parameters to QASM rotation angles
    theta_J = 2.0 * J
    theta_h = 2.0 * h
    theta_b = 2.0 * b
    
    def apply_u_block(q_n: int, q_n1: int):
        """
        Constructs the symmetric U_{n, n+1} block mapped from Equation (S5).
        q_n corresponds to the bottom wire, q_n1 corresponds to the top wire.
        """
        # 1. RZ(2h) on bottom wire (q_n)
        qasm_lines.append(f"rz({theta_h}) q[{q_n}];")
        
        # 2. RZZ(2J) decomposed into CX - RZ - CX
        qasm_lines.append(f"cx q[{q_n}],q[{q_n1}];")
        qasm_lines.append(f"rz({theta_J}) q[{q_n1}];")
        qasm_lines.append(f"cx q[{q_n}],q[{q_n1}];")
        
        # 3. RX(2b) on both wires
        qasm_lines.append(f"rx({theta_b}) q[{q_n}];")
        qasm_lines.append(f"rx({theta_b}) q[{q_n1}];")
        
        # 4. RZZ(2J) decomposed
        qasm_lines.append(f"cx q[{q_n}],q[{q_n1}];")
        qasm_lines.append(f"rz({theta_J}) q[{q_n1}];")
        qasm_lines.append(f"cx q[{q_n}],q[{q_n1}];")
        
        # 5. RZ(2h) on bottom wire (q_n)
        qasm_lines.append(f"rz({theta_h}) q[{q_n}];")
    
    def apply_external_block(q_n: int, q_n1: int):
        pass

    # Construct the Floquet stroboscopic evolution
    for layer in range(num_layers):
        qasm_lines.append(f"// --- Floquet Period {layer + 1} ---")
        
        # Even sub-layer (\hat{U}_e)
        qasm_lines.append("// Even Layer")
        for i in range(0, num_qubits - 1, 2):
            apply_u_block(i, i + 1)
            
        # Odd sub-layer (\hat{U}_o)
        qasm_lines.append("// Odd Layer")
        for i in range(1, num_qubits - 1, 2):
            apply_u_block(i, i + 1)

    return "\n".join(qasm_lines)

qasm_circuit = build_circuit_qasm(
    num_qubits=6, 
    num_layers=2, 
    J=np.pi/4, 
    h=np.pi/8, 
    b=0.2*np.pi
)