"""Execution module for running benchmarks with various engines."""

import time
from typing import Tuple, List, Dict, Any


from csbench.models import circuits, observables
from csbench.engines.abstract import BenchmarkEngine
from csbench.engines.statevector import StateVectorEngine
from csbench.engines.mpstab import MPStabEngine
from csbench.data_managing import build_results_path, save_benchmark_results


def get_engine(engine_name: str, **engine_kwargs) -> BenchmarkEngine:
    """
    Factory function to instantiate the appropriate benchmark engine.

    Args:
        engine_name: Name of the engine ("statevector" or "mpstab")
        **engine_kwargs: Additional kwargs to pass to the engine constructor

    Returns:
        An instantiated BenchmarkEngine subclass

    Raises:
        ValueError: If engine_name is not recognized
    """
    engines = {
        "statevector": StateVectorEngine,
        "mpstab": MPStabEngine,
    }

    if engine_name not in engines:
        raise ValueError(
            f"Engine '{engine_name}' not found. Available engines: {list(engines.keys())}"
        )

    return engines[engine_name](**engine_kwargs)


def get_observable(observable_name: str, nqubits: int) -> str:
    """
    Factory function to instantiate the appropriate observable.

    Args:
        observable_name: Name of the observable ("central_x" or "global_z")
        nqubits: Number of qubits

    Returns:
        Observable string representation

    Raises:
        ValueError: If observable_name is not recognized
    """
    obs_funcs = {
        "central_x": observables.central_x,
        "global_z": observables.global_z,
    }

    if observable_name not in obs_funcs:
        raise ValueError(
            f"Observable '{observable_name}' not found. Available observables: {list(obs_funcs.keys())}"
        )

    return obs_funcs[observable_name](nqubits)


def build_benchmark(
    engine_name: str,
    ansatz_name: str,
    nqubits: int,
    depth: int,
    n_circuits: int,
    rng_seed: int,
    magic_replacement_prob: float,
    observable_name: str,
    **engine_kwargs,
) -> Tuple[BenchmarkEngine, str, List, str]:
    """
    Build a complete benchmark by generating circuits, creating an observable,
    and instantiating an engine.

    Args:
        engine_name: Name of the engine to use ("statevector" or "mpstab")
        ansatz_name: Name of the circuit ansatz to generate
        nqubits: Number of qubits
        depth: Depth of the circuit
        n_circuits: Number of circuit variations to generate
        rng_seed: Random seed for reproducibility
        magic_replacement_prob: Probability of magic gate replacement
        observable_name: Name of the observable ("central_x" or "global_z")
        **engine_kwargs: Additional kwargs to pass to the engine constructor

    Returns:
        A tuple containing:
            - engine: Instantiated BenchmarkEngine
            - qasm_circuit: QASM string representation of the base circuit
            - sampled_parameters: List of parameter sets for circuit variations
            - observable: Observable string representation
    """
    # Generate circuit family
    qasm_circuit, sampled_parameters = circuits.generate_benchmark_circuits(
        ansatz_name=ansatz_name,
        nqubits=nqubits,
        depth=depth,
        n_circuits=n_circuits,
        rng_seed=rng_seed,
        magic_replacement_prob=magic_replacement_prob,
    )

    # Create the observable
    observable = get_observable(observable_name, nqubits)

    # Instantiate the engine
    engine = get_engine(engine_name, **engine_kwargs)

    return engine, qasm_circuit, sampled_parameters, observable


def run_benchmark(
    engine_name: str,
    ansatz_name: str,
    nqubits: int,
    depth: int,
    n_circuits: int,
    rng_seed: int,
    magic_replacement_prob: float,
    observable_name: str,
    base_results_dir: str = "results",
    simulation_kwargs: Dict[str, Any] = None,
    num_threads: int = 1,
    device_type: str = "cpu",
    precision: str = "float64",
    **engine_kwargs,
) -> Dict[str, Any]:
    """
    Run complete benchmark including circuit generation, execution, and result saving.

    Args:
        engine_name: Name of the engine to use
        ansatz_name: Name of the circuit ansatz
        nqubits: Number of qubits
        depth: Circuit depth
        n_circuits: Number of circuit variations
        rng_seed: Random seed
        magic_replacement_prob: Magic gate replacement probability
        observable_name: Name of the observable
        base_results_dir: Base results directory
        simulation_kwargs: Simulation configuration parameters (dict)
        num_threads: Number of CPU threads to use (default: 1)
        device_type: Device type - 'cpu', 'gpu', 'cuda', 'tpu' (default: 'cpu')
        precision: Numerical precision - 'float32' or 'float64' (default: 'float64')
        **engine_kwargs: Additional engine parameters

    Returns:
        Dictionary containing results path and summary statistics
    """
    if simulation_kwargs is None:
        simulation_kwargs = {}

    # Build benchmark
    engine, qasm_circuit, sampled_parameters, observable = build_benchmark(
        engine_name=engine_name,
        ansatz_name=ansatz_name,
        nqubits=nqubits,
        depth=depth,
        n_circuits=n_circuits,
        rng_seed=rng_seed,
        magic_replacement_prob=magic_replacement_prob,
        observable_name=observable_name,
        **engine_kwargs,
    )

    # # Configure machine environment (threading, device, precision)
    # configure_environment(
    #     simulation_engine=engine,
    #     num_threads=num_threads,
    #     device_type=device_type,
    #     precision=precision
    # )

    # Build results path
    results_path = build_results_path(
        ansatz_name=ansatz_name,
        observable_name=observable_name,
        nqubits=nqubits,
        depth=depth,
        magic_replacement_prob=magic_replacement_prob,
        engine_name=engine_name,
        base_results_dir=base_results_dir,
        statevector_backend=engine_kwargs.get("_qibo_backend_name"),
        statevector_platform=engine_kwargs.get("_qibo_platform_name"),
        simulation_kwargs=simulation_kwargs,
    )

    # Execute benchmarks
    execution_results = []
    for i, params in enumerate(sampled_parameters):
        print(f"Executing run {i}/{n_circuits}")
        expval, exec_time, fidelity = engine.expectation_value(
            qasm_circuit, params, observable
        )
        # Discarding the first, dry, run
        if i > 0:
            execution_results.append((expval, exec_time, fidelity))

    # Prepare metadata
    benchmark_metadata = {
        "engine_name": engine_name,
        "ansatz_name": ansatz_name,
        "observable_name": observable_name,
        "nqubits": nqubits,
        "depth": depth,
        "n_circuits": n_circuits,
        "rng_seed": rng_seed,
        "magic_replacement_prob": magic_replacement_prob,
        "engine_kwargs": engine_kwargs,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
    }

    # Save results
    saved_files = save_benchmark_results(
        results_path=results_path,
        benchmark_metadata=benchmark_metadata,
        execution_results=execution_results,
        qasm_circuit=qasm_circuit,
        sampled_parameters=sampled_parameters,
    )

    return {
        "results_path": str(results_path),
        "saved_files": saved_files,
        "num_executions": len(execution_results),
        "benchmark_metadata": benchmark_metadata,
    }
