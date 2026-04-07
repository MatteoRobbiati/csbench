from dataclasses import dataclass


@dataclass
class BenchmarkEngine:
    _device: str = "cpu"
    _precision: str = "float64"

    def expectation_value(self, circuit, observable) -> tuple[float, float, float]:
        """
        Compute the expectation value of the given observable on the given circuit.

        Returns a tuple containing the expectation value, the time taken to compute it, and the fidelity of the representation.
            If the method is exact, fidelity returned should be 1.
        """
        pass

    def simulation_configuration(self):
        """
        Set all the relevant simulation hyperparameters. For example, a Tensor Network based engine might want to set
        the maximum bond dimension.
        """
        pass

    def set_machine_parameters(self, device: str = "cpu", precision: str = "float64"):
        """
        Set the machine parameters for the simulation. This can include the device to run on (e.g., "cpu", "cuda", "tpu") and the precision (e.g., "float32", "float64").
        """
        self._device = device
        self._precision = precision

    @property
    def device(self):
        return self._device

    @property
    def precision(self):
        return self._precision
