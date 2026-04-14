"""
Circuit generation module. All the circuits are generated with angles equal to zero.
The gates we don't want to be trainable (we want to fix the angles) has to be 
set as non trainable during circuit construction.
"""

import sys

import random
import numpy as np
from copy import deepcopy
from qibo import Circuit, gates

# We want to use mpstab's ansatze to tune the magic
from mpstab.models.ansatze import CircuitAnsatz


def hardware_efficient(nqubits: int, depth: int) -> str:
    """
    Generate a simple string corresponding to an hardware efficient ansatz.
    This Hardware Efficient Ansatz consists of alternating layers of single-qubit RY rotations and CZ entangling gates.
    """
    circuit = Circuit(nqubits)
    for d in range(depth):
        for q in range(nqubits):
            circuit.add(gates.RY(q, theta=0.0))
        for q in range(nqubits - 1):
            circuit.add(gates.CZ(q % nqubits, (q + 1) % nqubits))
    return circuit


def floquet_dynamics(nqubits: int, depth: int) -> str:
    """Ciao"""
    pass


def generate_benchmark_circuits(
    ansatz_name: str,
    nqubits: int,
    depth: int,
    n_circuits: int,
    rng_seed: int,
    magic_replacement_prob: float,
) -> tuple[str, list[str]]:
    """Generate a family of circuits which will be run to compute the statistics requirewd for the benchmark."""

    # Check that the provided name corresponds to a valid ansatz function defined in this module
    if ansatz_name not in list(sys.modules[__name__].__dict__.keys()):
        raise ValueError(
            f"Ansatz {ansatz_name} not found. Available ansatze are: {list(sys.modules[__name__].__dict__.keys())}"
        )

    # Collect all the sub modules of the current module
    current_module = sys.modules[__name__]

    # Fixing seed to ensure reproducibility
    random.seed(rng_seed)
    np.random.seed(rng_seed)

    reference_circuit = getattr(current_module, ansatz_name)(nqubits, depth)
    qasm_circuit = reference_circuit.to_qasm()

    sampled_parameters = []
    for _ in range(n_circuits + 1):
        circuit = deepcopy(reference_circuit)

        circuit.set_parameters(
            np.random.uniform(0, 2 * np.pi, size=len(circuit.get_parameters()))
        )

        circuit_ansatz = CircuitAnsatz(qibo_circuit=circuit)

        # Partitioning the circuit sampled from the theoretical distribution
        # of the original circuit
        _, sampled_circuit = circuit_ansatz.partitionate_circuit(
            replacement_probability=magic_replacement_prob, replacement_method="closest"
        )

        sampled_parameters.append(sampled_circuit.get_parameters())

    return qasm_circuit, sampled_parameters
