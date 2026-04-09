"""Generates simple strings corresponding to our target observables."""

import numpy as np
from functools import lru_cache
from scipy import sparse

from qibo import matrices
from qibo.hamiltonians import Hamiltonian


@lru_cache(maxsize=128)
def central_x(
    nqubits: int, as_symbolic: bool = False, use_sparse: bool = True
) -> str | Hamiltonian:
    """
    Return the central X observable for a given number of qubits.
    This generator is usable only if an odd number of qubits is chosen.

    Uses sparse matrix representation for efficiency with larger qubit counts.
    """

    if nqubits % 2 == 0:
        raise ValueError("Number of qubits must be odd to have a central X observable.")

    if as_symbolic:
        central_qubit = nqubits // 2
        dim = 2**nqubits

        if use_sparse:
            # Build sparse matrix for I^(central_qubit) ⊗ X ⊗ I^(nqubits - central_qubit - 1)
            # For X gate at position k: it swaps basis states that differ only at position k
            # Create a list of (row, col, data) for the sparse matrix
            rows = []
            cols = []
            data = []

            # Iterate through all basis states
            for state in range(dim):
                # Flip the bit at the central position
                flipped_state = state ^ (1 << central_qubit)
                rows.append(state)
                cols.append(flipped_state)
                data.append(1)

            # Create sparse COO matrix and convert to CSR for efficiency
            matrix = sparse.coo_matrix((data, (rows, cols)), shape=(dim, dim)).tocsr()
        else:
            # Build dense matrix using kronecker products
            qubit_before = central_qubit
            qubit_after = nqubits - central_qubit - 1

            # I^(central_qubit) ⊗ X ⊗ I^(nqubits - central_qubit - 1)
            matrix = np.kron(
                np.eye(2**qubit_before), np.kron(matrices.X, np.eye(2**qubit_after))
            )
        return Hamiltonian(nqubits, matrix)

    obs = "I" * int(nqubits / 2) + "X" + "I" * int(nqubits / 2)
    return obs


@lru_cache(maxsize=128)
def global_z(
    nqubits: int, as_symbolic: bool = False, use_sparse: bool = True
) -> str | Hamiltonian:
    """
    Return the global Z observable for a given number of qubits.

    Uses sparse diagonal matrix representation for efficiency with larger qubit counts.
    The matrix is diagonal with eigenvalues ±1 based on qubit parity.
    """
    if not as_symbolic:
        obs = "Z" * nqubits
        return obs

    dim = 2**nqubits

    if use_sparse:
        # Build sparse diagonal matrix for Z ⊗ Z ⊗ ... ⊗ Z
        diagonal = np.zeros(dim, dtype=np.float64)

        # For each basis state |b_0 b_1 ... b_n⟩:
        # (Z⊗Z⊗...⊗Z)|b_0 b_1 ... b_n⟩ = (-1)^(sum of bits) |b_0 b_1 ... b_n⟩
        for state in range(dim):
            # Count the number of 1s in the binary representation
            num_ones = bin(state).count("1")
            diagonal[state] = (-1) ** num_ones

        # Create sparse diagonal matrix
        matrix = sparse.diags(diagonal, format="csr")
    else:
        # Build dense matrix using kronecker products of Z matrices
        matrix = matrices.Z
        for _ in range(nqubits - 1):
            matrix = np.kron(matrix, matrices.Z)

    return Hamiltonian(nqubits, matrix)
