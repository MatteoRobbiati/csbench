import time

from dataclasses import dataclass

from qibo import Circuit
from mpstab.evolutors.hsmpo import HSMPO

from csbench.engines.abstract import BenchmarkEngine


@dataclass
class MPStabEngine(BenchmarkEngine):
    max_bond_dimension: float = None

    def expectation_value(self, qasm_circuit, parameters, observable):
        """
        Compute the expectation value of the given observable on the given circuit.

        """

        circuit = Circuit.from_qasm(qasm_circuit)
        circuit.set_parameters(parameters)

        surrogate = HSMPO(circuit, max_bond_dimension=self.max_bond_dimension)

        initial_time = time.time()
        expval = surrogate.expectation(observable=observable, return_fidelity=False)
        final_time = time.time()

        fidelity = surrogate.truncation_fidelity(
            replacement_probability=0.0,
        )

        return expval, final_time - initial_time, fidelity
