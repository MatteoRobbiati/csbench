import time
from dataclasses import dataclass

from qibo import Circuit, construct_backend
from qibo.backends import Backend

from csbench.engines.abstract import BenchmarkEngine
from csbench.utils import obs_string_to_qibo_hamiltonian

@dataclass
class StateVectorEngine(BenchmarkEngine):

    _qibo_backend_name: str = "numpy"
    _qibo_platform_name: str = None
    _qibo_backend: Backend = None

    def __post_init__(self):
        self.set_qibo_backend(self._qibo_backend_name, self._qibo_platform_name)

    def expectation_value(self, qasm_circuit, parameters, observable):
        """
        Compute the expectation value of the given observable on the given circuit.
        
        """
        circuit = Circuit.from_qasm(qasm_circuit)
        circuit.set_parameters(parameters)

        # Constructing a Qibo observable
        hamiltonian = obs_string_to_qibo_hamiltonian(observable, self._qibo_backend)

        initial_time = time.time()
        statevector = circuit().state()
        expval = hamiltonian.expectation_from_state(statevector)
        final_time = time.time()

        return expval, final_time - initial_time, 1.0
    
    @property
    def qibo_backend(self):
        return self._qibo_backend
    
    @property
    def qibo_platform(self):
        return self._qibo_platform
    
    def set_qibo_backend(self, backend: str = "numpy", platform: str = None):
        """
        Set the Qibo backend and platform for the simulation. This can include the device to run on (e.g., "numpy", "tensorflow", "jax") and the platform (e.g., "cpu", "cuda", "tpu").
        """
        self._qibo_backend = backend
        self._qibo_platform = platform
        self._qibo_backend = construct_backend(backend=backend, platform=platform)
