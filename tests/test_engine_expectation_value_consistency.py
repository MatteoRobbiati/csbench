import numpy as np
import pytest
from qibo import Circuit, gates

pytest.importorskip("quimb")

from csbench.engines.mpstab import MPStabEngine
from csbench.engines.quimb import QuimbEngine


def _build_test_case() -> tuple[str, np.ndarray, str]:
    """Create a small parameterized circuit shared by both engines."""
    circuit = Circuit(3)
    circuit.add(gates.RY(0, theta=0.0))
    circuit.add(gates.CZ(0, 1))
    circuit.add(gates.RY(1, theta=0.0))
    circuit.add(gates.CZ(1, 2))

    qasm_circuit = circuit.to_qasm()
    parameters = np.array([0.37, 1.11], dtype=float)
    observable = "IXI"

    return qasm_circuit, parameters, observable


def test_quimb_and_mpstab_expectation_values_match():
    qasm_circuit, parameters, observable = _build_test_case()
    max_bond_dimension = 8

    quimb_engine = QuimbEngine(max_bond_dimension=max_bond_dimension)
    mpstab_engine = MPStabEngine(max_bond_dimension=max_bond_dimension)

    quimb_expval, _, _ = quimb_engine.expectation_value(
        qasm_circuit=qasm_circuit,
        parameters=parameters,
        observable=observable,
    )
    mpstab_expval, _, _ = mpstab_engine.expectation_value(
        qasm_circuit=qasm_circuit,
        parameters=parameters,
        observable=observable,
    )

    assert float(np.real(quimb_expval)) == pytest.approx(
        float(np.real(mpstab_expval)), rel=1e-8, abs=1e-8
    )
