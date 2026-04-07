
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
            circuit.add(gates.RY(q, theta=0.1))
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
        n_circuits:int
    )->tuple[str, list[str]]:
    """Generate a family of circuits which will be run to compute the statistics requirewd for the benchmark."""
    


