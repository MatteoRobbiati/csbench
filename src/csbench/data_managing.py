"""Data management module for handling benchmark results and file I/O."""

import json
import time
from pathlib import Path
from typing import List, Dict, Tuple, Any

import numpy as np
from scipy.stats import median_abs_deviation


def build_results_path(
    ansatz_name: str,
    observable_name: str,
    nqubits: int,
    depth: int,
    magic_replacement_prob: float,
    engine_name: str,
    base_results_dir: str = "results",
    statevector_backend: str = None,
    statevector_platform: str = None,
    simulation_kwargs: Dict[str, Any] = None,
) -> Path:
    """
    Build the results directory path following the structure:
    results/{ansatz}_{observable}/qubits{nqubits}_layers{depth}_repl_prob{magic_replacement_prob}/{engine}/
    
    For statevector engine, appends backend and platform to engine name.
    For engines with simulation kwargs, appends them to the engine name.
    
    Args:
        ansatz_name: Name of the circuit ansatz
        observable_name: Name of the observable
        nqubits: Number of qubits
        depth: Circuit depth
        magic_replacement_prob: Magic replacement probability
        engine_name: Name of the engine
        base_results_dir: Base results directory (default: "results")
        statevector_backend: Backend for statevector engine (optional)
        statevector_platform: Platform for statevector engine (optional)
        simulation_kwargs: Simulation configuration parameters (dict, optional)
        
    Returns:
        Path object pointing to the results directory
    """
    # Create subdirectory names
    ansatz_obs_dir = f"{ansatz_name}_{observable_name}"
    params_dir = f"qubits{nqubits}_layers{depth}_repl_prob{magic_replacement_prob:.2f}"
    
    # Build engine directory name with backend/platform for statevector
    engine_dir = engine_name
    if engine_name == "statevector" and statevector_backend:
        engine_dir = f"{engine_name}_{statevector_backend}"
        if statevector_platform:
            engine_dir = f"{engine_dir}_{statevector_platform}"
    
    # Add simulation kwargs to engine directory name
    if simulation_kwargs:
        kwargs_str = "_".join([f"{k}{v}" for k, v in sorted(simulation_kwargs.items())])
        engine_dir = f"{engine_dir}_{kwargs_str}"
    
    results_path = Path(base_results_dir) / ansatz_obs_dir / params_dir / engine_dir
    results_path.mkdir(parents=True, exist_ok=True)
    
    return results_path


def save_benchmark_results(
    results_path: Path,
    benchmark_metadata: Dict[str, Any],
    execution_results: List[Tuple[float, float, float]],
    qasm_circuit: str,
    sampled_parameters: List[Any],
) -> Dict[str, str]:
    """
    Save benchmark execution results and metadata to disk.
    
    Args:
        results_path: Path to the results directory
        benchmark_metadata: Dictionary containing benchmark configuration and parameters
        execution_results: List of tuples (expval, time, fidelity) from engine executions
        qasm_circuit: QASM string representation of the circuit
        sampled_parameters: List of parameter sets for each execution
        
    Returns:
        Dictionary with paths to saved files
    """
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    
    # Create parameters subdirectory
    parameters_dir = results_path / "parameters"
    parameters_dir.mkdir(parents=True, exist_ok=True)
    
    # Save metadata
    metadata_file = results_path / f"metadata_{timestamp}.json"
    with open(metadata_file, "w") as f:
        json.dump(benchmark_metadata, f, indent=2)
    
    # Save circuit QASM
    circuit_file = results_path / f"circuit_{timestamp}.qasm"
    with open(circuit_file, "w") as f:
        f.write(qasm_circuit)
    
    # Save sampled parameters as numpy arrays
    parameters_file = parameters_dir / f"parameters_{timestamp}.npz"
    # Create a dictionary with each parameter set indexed
    params_dict = {f"param_set_{i}": np.asarray(param_set) for i, param_set in enumerate(sampled_parameters)}
    np.savez(parameters_file, **params_dict)
    
    # Save execution results
    results_file = results_path / f"results_{timestamp}.json"
    results_data = {
        "num_executions": len(execution_results),
        "executions": [
            {
                "expectation_value": float(expval),
                "execution_time_seconds": float(exec_time),
                "fidelity": float(fidelity)
            }
            for expval, exec_time, fidelity in execution_results
        ]
    }
    
    # Compute statistics
    expvals = np.array([r[0] for r in execution_results])
    times = np.array([r[1] for r in execution_results])
    fidelities = np.array([r[2] for r in execution_results])
    
    results_data["statistics"] = {
        "expectation_value": {
            "median": float(np.median(expvals)),
            "mad": float(median_abs_deviation(expvals)),
        },
        "execution_time": {
            "median": float(np.median(times)),
            "mad": float(median_abs_deviation(times)),
            "total": float(np.sum(times))
        },
        "fidelity": {
            "median": float(np.median(fidelities)),
            "mad": float(median_abs_deviation(fidelities)),
        }
    }
    
    with open(results_file, "w") as f:
        json.dump(results_data, f, indent=2)
    
    return {
        "metadata": str(metadata_file),
        "circuit": str(circuit_file),
        "parameters": str(parameters_file),
        "results": str(results_file)
    }
