import time
from dataclasses import dataclass
from qibo import Circuit
from qibo.gates.abstract import ParametrizedGate
from quimb.tensor import CircuitMPS
from quimb import pauli
from csbench.engines.abstract import BenchmarkEngine

GATE_MAP = {
    "h": "H",
    "x": "X",
    "y": "Y",
    "z": "Z",
    "s": "S",
    "t": "T",
    "rx": "RX",
    "ry": "RY",
    "rz": "RZ",
    "u3": "U3",
    "cx": "CX",
    "cnot": "CNOT",
    "cy": "CY",
    "cz": "CZ",
    "iswap": "ISWAP",
    "swap": "SWAP",
    "ccx": "CCX",
    "ccy": "CCY",
    "ccz": "CCZ",
    "toffoli": "TOFFOLI",
    "cswap": "CSWAP",
    "fredkin": "FREDKIN",
    "fsim": "fsim",
    "measure": "measure",
}

def _qibo_circuit_to_quimb(nqubits, qibo_circ, **circuit_kwargs):
    """
    Convert a Qibo Circuit to a Quimb Circuit. Measurement gates are ignored. If are given gates not supported by Quimb, an error is raised.

    Parameters
    ----------
    qibo_circ : qibo.models.circuit.Circuit
        The circuit to convert.
    quimb_circuit_type : type
        The Quimb circuit class to use (Circuit, CircuitMPS, etc).
    circuit_kwargs : dict
        Extra arguments to pass to the Quimb circuit constructor.

    Returns
    -------
    circ : quimb.tensor.circuit.Circuit
        The converted circuit.
    """

    circ = CircuitMPS(nqubits, **circuit_kwargs)

    for gate in qibo_circ.queue:
        gate_name = getattr(gate, "name", None)
        quimb_gate_name = GATE_MAP.get(gate_name, None)
        if quimb_gate_name == "measure":
            continue
        if quimb_gate_name is None:
            raise ValueError(f"Gate {gate_name} not supported in Quimb backend.")

        params = getattr(gate, "parameters", ())
        qubits = getattr(gate, "qubits", ())

        is_parametrized = isinstance(gate, ParametrizedGate) and getattr(
            gate, "trainable", True
        )
        if is_parametrized:
            circ.apply_gate(
                quimb_gate_name, *params, *qubits, parametrized=is_parametrized
            )
        else:
            circ.apply_gate(
                quimb_gate_name,
                *params,
                *qubits,
            )

    return circ


@dataclass
class QuimbEngine(BenchmarkEngine):

    max_bond_dimension:float = None

    def expectation_value(self, qasm_circuit, parameters, observable):
        """
        Compute the expectation value of the given observable on the given circuit.
        """
        circuit = Circuit.from_qasm(qasm_circuit)
        circuit.set_parameters(parameters)


        initial_time = time.time()
        
        # Construction is computationally heavy, fair to time it.
        psi_ket = _qibo_circuit_to_quimb(
            nqubits=circuit.nqubits, 
            qibo_circ=circuit, 
            max_bond=self.max_bond_dimension
            ).psi
        
        non_i_ops = {i: op.upper() for i, op in enumerate(observable) if op.upper() != "I"}
        psi_op = psi_ket.copy()
        for site, label in non_i_ops.items():
            psi_op.gate_(pauli(label), site)

        expval = (psi_ket.H & psi_op).contract(optimize="auto-hq").real

        final_time = time.time()

        # Out of timing, we need to reconstruct the lost state for computing fidelity
        psi_ket = _qibo_circuit_to_quimb(
            nqubits=circuit.nqubits, 
            qibo_circ=circuit, 
            max_bond=self.max_bond_dimension
            )
        fidelity = psi_ket.fidelity_estimate()

        return expval, final_time - initial_time, fidelity
