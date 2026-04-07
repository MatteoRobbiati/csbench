"""Generates simple strings corresponding to our target observables."""


def central_x(nqubits:int)->str:
    """
    Return the central X observable for a given number of qubits.
    This generator is usable only if an odd number of qubits is chosen.
    """

    if nqubits % 2 == 0:
        raise ValueError("Number of qubits must be odd to have a central X observable.")
    obs_str = "I" * int(nqubits / 2) + "X" + "I" * int(nqubits / 2)
    return obs_str


def global_z(nqubits:int)->str:
    """
    Return the global Z observable for a given number of qubits.
    """
    obs_str = "Z" * nqubits
    return obs_str