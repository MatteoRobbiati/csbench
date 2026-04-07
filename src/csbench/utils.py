from qibo import hamiltonians, symbols
from qibo.backends import Backend
import json
from typing import Dict, Any


def count_magic_gates(qibo_circuit):

    magic_gates = 0
    for gate in qibo_circuit.queue:
        if not gate.clifford:
            magic_gates += 1
    
    return magic_gates


def parse_simulation_kwargs(kwargs_str: str) -> Dict[str, Any]:
    """
    Parse simulation kwargs from a string format.
    
    Supports two formats:
    1. JSON format: '{"max_bond_dim": 256, "precision": 64}'
    2. Key-value format: 'max_bond_dimension=256,precision=64'
    
    Values are automatically converted to appropriate types (int, float, or str).
    
    Args:
        kwargs_str: String representation of simulation kwargs
        
    Returns:
        Dictionary with parsed kwargs
    """
    if not kwargs_str:
        return {}
    
    # Try to parse as JSON first
    if kwargs_str.startswith('{'):
        return json.loads(kwargs_str)
    
    # Parse as key=value pairs
    kwargs_dict = {}
    for pair in kwargs_str.split(','):
        key, val = pair.split('=')
        key = key.strip()
        val = val.strip()
        
        # Try to convert to appropriate type
        try:
            kwargs_dict[key] = int(val)
        except ValueError:
            try:
                kwargs_dict[key] = float(val)
            except ValueError:
                kwargs_dict[key] = val
    
    return kwargs_dict


def obs_string_to_qibo_hamiltonian(observable: str, qibo_backend: Backend) -> hamiltonians.SymbolicHamiltonian:
    """
    Convert a string representation of a Pauli observable to a Qibo symbolic Hamiltonian.

    Args:
        observable (str): A string representing the Pauli observable, e.g., "XZIY".

    Returns:
        hamiltonians.SymbolicHamiltonian: The corresponding Qibo symbolic Hamiltonian.
    """
    form = 1
    for i, pauli in enumerate(observable):
        form *= getattr(symbols, pauli)(i)
    ham = hamiltonians.SymbolicHamiltonian(form=form, backend=qibo_backend)
    return ham