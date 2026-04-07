
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






